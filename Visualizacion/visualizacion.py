"""
Dashboard de Visualización - Pull Requests en GitHub (2020-2024)
Fuente de datos: Madnight GitHub Hut
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import numpy as np

# ============================================================================
# CARGA Y PREPARACIÓN DE DATOS
# ============================================================================

print("Cargando datos...")
df = pd.read_csv('Datos_procesados/MadnightPullRequests_cleaned.csv')

print(f"Datos cargados: {len(df)} registros")
print(f"Período: {df['Año'].min()} - {df['Año'].max()}")
print(f"Lenguajes únicos: {df['Lenguaje'].nunique()}")

# ============================================================================
# PREGUNTA 1: Top lenguajes en Ranking #1 por año
# ============================================================================

def crear_grafico_top_lenguajes():
    """
    ¿Cuál es el lenguaje de programación con más pull request en el Top 1 
    a lo largo de todos los años registrados?
    """
    # Filtrar solo los registros con Ranking = 1
    top1_df = df[df['Ranking'] == 1].copy()
    
    # Contar cuántas veces cada lenguaje fue Top 1 dentro de cada año
    top1_por_anio = (
        top1_df
        .groupby(['Año', 'Lenguaje'])
        .size()
        .reset_index(name='Veces_Top1_en_Anio')
    )

    # Para cada año, quedarnos con el lenguaje que más veces fue Top 1
    top1_anual = (
        top1_por_anio
        .sort_values(['Año', 'Veces_Top1_en_Anio'], ascending=[True, False])
        .groupby('Año')
        .head(1)
    )

    top1_count = (
        top1_anual
        .groupby('Lenguaje')
        .size()
        .reset_index(name='Años_en_Top1')
        .sort_values('Años_en_Top1', ascending=True)
    )
    
    # Crear gráfico de barras horizontales
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top1_count['Lenguaje'],
        x=top1_count['Años_en_Top1'],
        orientation='h',
        marker=dict(
            color=top1_count['Años_en_Top1'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Años<br>Top 1")
        ),
        text=top1_count['Años_en_Top1'],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>' +
                      'Años en Top 1: %{x}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Lenguajes con Más Pull Requests en el Top 1 (2020-2024)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis_title='Conteo-Años en Top 1',
        yaxis_title='Lenguaje de Programación',
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['1-2020', '2-2021', '3-2022', '4-2023', '5-2024']
        ),
        height=400,
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        paper_bgcolor='white',
        font=dict(size=12),
        hovermode='closest',
        margin=dict(l=100, r=50, t=80, b=50)
    )
    
    # Agregar línea de referencia
    max_count = top1_count['Años_en_Top1'].max()
    fig.add_vline(x=max_count, line_dash="dash", line_color="red", 
                  annotation_text=f"Máximo: {max_count}", 
                  annotation_position="top right")
    
    return fig

# ============================================================================
# PREGUNTA 2: Heatmap de porcentajes por año y quarter
# ============================================================================

def crear_heatmap_quarters():
    """
    ¿Cuál es el porcentaje de pull requests que ha tenido cada lenguaje 
    de programación a lo largo de los años por trimestres 2020-2024?
    """
    # Seleccionar los top 15 lenguajes más populares (por promedio de porcentaje)
    top_languages = df.groupby('Lenguaje')['Porcentaje'].mean().nlargest(15).index.tolist()
    
    df_filtered = df[df['Lenguaje'].isin(top_languages)].copy()
    
    # Crear columna de período
    df_filtered['Periodo'] = df_filtered['Año'].astype(str) + '-Q' + df_filtered['Quarter'].astype(str)
    
    # Crear matriz pivot
    heatmap_data = df_filtered.pivot_table(
        index='Lenguaje',
        columns='Periodo',
        values='Porcentaje',
        aggfunc='mean'
    )
    
    # Ordenar por promedio general
    heatmap_data['promedio'] = heatmap_data.mean(axis=1)
    heatmap_data = heatmap_data.sort_values('promedio', ascending=False)
    heatmap_data = heatmap_data.drop('promedio', axis=1)
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='RdYlGn',
        text=np.round(heatmap_data.values, 2),
        texttemplate='%{text}%',
        textfont={"size": 9},
        colorbar=dict(title="Porcentaje<br>PR (%)")
    ))
    
    fig.update_layout(
        title={
            'text': 'Heatmap: Porcentaje de Pull Requests por Quarter (Top 15 Lenguajes)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis_title='Período (Año-Quarter)',
        yaxis_title='Lenguaje de Programación',
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis={'side': 'bottom'},
        font=dict(size=11)
    )
    
    return fig

# ============================================================================
# PREGUNTA 3: Medidores de promedio general
# ============================================================================

def crear_medidores_promedio():
    """
    ¿Cuál es el promedio general de pull requests para cada uno de los 
    lenguajes de programación en el periodo de estudio 2020-2024?
    """
    # Calcular promedio por lenguaje (top 10)
    promedio_df = df.groupby('Lenguaje')['Porcentaje'].mean().reset_index()
    promedio_df = promedio_df.sort_values('Porcentaje', ascending=False).head(10)
    
    # Crear subplots con medidores
    from plotly.subplots import make_subplots
    
    # Calcular el valor máximo para la escala
    max_val = promedio_df['Porcentaje'].max() * 1.2
    
    # Crear 2 filas de 5 columnas
    fig = make_subplots(
        rows=2, cols=5,
        specs=[[{'type': 'indicator'}] * 5] * 2,
        subplot_titles=promedio_df['Lenguaje'].tolist()
    )
    
    # Añadir cada medidor
    for idx, (_, row) in enumerate(promedio_df.iterrows(), 1):
        row_num = (idx - 1) // 5 + 1
        col_num = (idx - 1) % 5 + 1
        
        # Determinar color según el valor
        if row['Porcentaje'] > 10:
            color = "#27ae60"  # Verde
        elif row['Porcentaje'] > 5:
            color = "#f39c12"  # Amarillo
        else:
            color = "#e74c3c"  # Rojo
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=row['Porcentaje'],
                number={'suffix': "%", 'font': {'size': 20}},
                delta={'reference': promedio_df['Porcentaje'].mean()},
                gauge={
                    'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "darkgray"},
                    'bar': {'color': color},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, max_val * 0.33], 'color': '#fadbd8'},
                        {'range': [max_val * 0.33, max_val * 0.66], 'color': '#fdebd0'},
                        {'range': [max_val * 0.66, max_val], 'color': '#d5f4e6'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': promedio_df['Porcentaje'].mean()
                    }
                }
            ),
            row=row_num, col=col_num
        )
    
    fig.update_layout(
        title={
            'text': 'Promedio General de Pull Requests por Lenguaje (2020-2024)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        height=600,
        showlegend=False,
        paper_bgcolor='white',
        font=dict(size=10)
    )
    
    return fig

# ============================================================================
# CREACIÓN DEL DASHBOARD
# ============================================================================

# Inicializar la aplicación Dash
app = Dash(__name__)
app.title = "Dashboard Pull Requests GitHub"

# Estilos CSS
colors = {
    'background': '#f5f7fa',
    'text': '#2c3e50',
    'card': '#ffffff',
    'accent': '#3498db'
}

# Layout del dashboard
app.layout = html.Div(style={'backgroundColor': colors['background'], 'fontFamily': 'Arial, sans-serif'}, children=[
    
    # Header
    html.Div(style={
        'backgroundColor': colors['accent'],
        'padding': '30px',
        'marginBottom': '30px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }, children=[
        html.H1(
            'Dashboard de Pull Requests en GitHub',
            style={
                'color': 'white',
                'textAlign': 'center',
                'margin': '0',
                'fontSize': '36px'
            }
        ),
        html.P(
            'Análisis de tendencias de lenguajes de programación (2020-2024)',
            style={
                'color': 'white',
                'textAlign': 'center',
                'margin': '10px 0 0 0',
                'fontSize': '16px',
                'opacity': '0.9'
            }
        ),
        html.P(
            'Fuente: Madnight GitHub Hut',
            style={
                'color': 'white',
                'textAlign': 'center',
                'margin': '5px 0 0 0',
                'fontSize': '12px',
                'opacity': '0.7'
            }
        )
    ]),
    
    # Contenedor principal
    html.Div(style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '20px'}, children=[
        
        # Tarjeta de estadísticas generales
        html.Div(style={
            'backgroundColor': colors['card'],
            'padding': '20px',
            'marginBottom': '30px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
        }, children=[
            html.H3('📊 Resumen de Datos', style={'color': colors['text'], 'marginBottom': '15px'}),
            html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap'}, children=[
                html.Div([
                    html.H2(f"{len(df)}", style={'color': colors['accent'], 'margin': '0'}),
                    html.P('Registros Totales', style={'color': colors['text'], 'margin': '5px 0'})
                ]),
                html.Div([
                    html.H2(f"{df['Lenguaje'].nunique()}", style={'color': colors['accent'], 'margin': '0'}),
                    html.P('Lenguajes Analizados', style={'color': colors['text'], 'margin': '5px 0'})
                ]),
                html.Div([
                    html.H2('5 años', style={'color': colors['accent'], 'margin': '0'}),
                    html.P('Período de Estudio', style={'color': colors['text'], 'margin': '5px 0'})
                ]),
                html.Div([
                    html.H2('20 quarters', style={'color': colors['accent'], 'margin': '0'}),
                    html.P('Períodos Trimestrales', style={'color': colors['text'], 'margin': '5px 0'})
                ])
            ])
        ]),
        
        # Pregunta 1: Gráfico de Barras Top
        html.Div(style={
            'backgroundColor': colors['card'],
            'padding': '25px',
            'marginBottom': '30px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
        }, children=[
            # html.H3(
            #     'Pregunta 1: ¿Cuál es el lenguaje con más pull requests en el Top 1?',
            #     style={'color': colors['text'], 'marginBottom': '20px'}
            # ),
            dcc.Graph(
                id='grafico-top-lenguajes',
                figure=crear_grafico_top_lenguajes(),
                config={'displayModeBar': False}
            )
        ]),
        
        # Pregunta 2: Heatmap
        html.Div(style={
            'backgroundColor': colors['card'],
            'padding': '25px',
            'marginBottom': '30px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
        }, children=[
            # html.H3(
            #     'Pregunta 2: ¿Porcentaje de pull requests por trimestre y año?',
            #     style={'color': colors['text'], 'marginBottom': '20px'}
            # ),
            dcc.Graph(
                id='heatmap-quarters',
                figure=crear_heatmap_quarters(),
                config={'displayModeBar': False}
            )
        ]),
        
        # Pregunta 3: Medidores
        html.Div(style={
            'backgroundColor': colors['card'],
            'padding': '25px',
            'marginBottom': '30px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
        }, children=[
            # html.H3(
            #     'Pregunta 3: ¿Promedio general de pull requests por lenguaje?',
            #     style={'color': colors['text'], 'marginBottom': '20px'}
            # ),
            dcc.Graph(
                id='medidores-promedio',
                figure=crear_medidores_promedio(),
                config={'displayModeBar': False}
            )
        ]),
        
        # Footer
        html.Div(style={
            'textAlign': 'center',
            'padding': '20px',
            'color': colors['text'],
            'opacity': '0.7'
        }, children=[
            html.P('© 2025 | Proyecto de Análisis de Datos | Tecnología: Dash + Plotly'),
            html.P('Datos extraídos mediante web scraping con Selenium WebDriver y Nokogiri (Ruby)')
        ])
    ])
])

# ============================================================================
# EJECUTAR SERVIDOR
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  DASHBOARD INICIADO")
    print("="*70)
    print(f"\n  Accede al dashboard en: http://127.0.0.1:8050/")
    print(f"\n  Presiona CTRL+C para detener el servidor\n")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8050)