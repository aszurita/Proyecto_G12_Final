"""
Dashboard de Visualización - Pull Requests en GitHub (2020-2024)
Fuente de datos: Madnight GitHub Hut
Análisis enfocado en 15 lenguajes principales
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
df_original = pd.read_csv('Datos_procesados/MadnightPullRequests_cleaned.csv')

# ============================================================================
# FILTRO DE LENGUAJES ESPECÍFICOS
# ============================================================================

# Lista de lenguajes a analizar (definida por el equipo)
LENGUAJES_SELECCIONADOS = [
    'Python', 'C', 'C++', 'C#', 'Java', 'JavaScript', 
    'Assembly', 'R', 'Perl', 'Fortran', 'Rust', 
    'MATLAB', 'PHP', 'Go', 'Kotlin'
]

# Filtrar el dataframe para incluir solo los lenguajes seleccionados
df = df_original[df_original['Lenguaje'].isin(LENGUAJES_SELECCIONADOS)].copy()

print(f"Datos cargados: {len(df)} registros (filtrados de {len(df_original)})")
print(f"Período: {df['Año'].min()} - {df['Año'].max()}")
print(f"Lenguajes analizados: {df['Lenguaje'].nunique()} de 15 seleccionados")
print(f"Lenguajes incluidos: {sorted(df['Lenguaje'].unique())}")

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

def crear_heatmap_quarters(anio_seleccionado='Todos', num_lenguajes=15):
    """
    ¿Cuál es el porcentaje de pull requests que ha tenido cada lenguaje 
    de programación a lo largo de los años por trimestres 2020-2024?
    
    Ahora con selector de año para análisis detallado
    """
    # Filtrar por año si no es "Todos"
    if anio_seleccionado == 'Todos':
        df_filtered = df.copy()
        titulo_anio = "Todos los Años (2020-2024)"
    else:
        df_filtered = df[df['Año'] == int(anio_seleccionado)].copy()
        titulo_anio = f"Año {anio_seleccionado}"
    
  
    # Crear columna de período
    if anio_seleccionado == 'Todos':
        df_filtered['Periodo'] = df_filtered['Año'].astype(str) + '-Q' + df_filtered['Quarter'].astype(str)
    else:
        # Solo mostrar quarters cuando es un año específico
        df_filtered['Periodo'] = 'Q' + df_filtered['Quarter'].astype(str)
    
    # Crear matriz pivot
    heatmap_data = df_filtered.pivot_table(
        index='Lenguaje',
        columns='Periodo',
        values='Porcentaje',
        aggfunc='mean'
    )
    
    heatmap_data = heatmap_data.fillna(0)

    # Ordenar columnas (quarters o períodos)
    if anio_seleccionado != 'Todos':
        quarter_order = ['Q1', 'Q2', 'Q3', 'Q4']
        heatmap_data = heatmap_data[[col for col in quarter_order if col in heatmap_data.columns]]
    
    # Ordenar por promedio general
    heatmap_data['promedio'] = heatmap_data.mean(axis=1)
    heatmap_data = heatmap_data.sort_values('promedio', ascending=False)
    
    if num_lenguajes < 15:
        heatmap_data = heatmap_data.head(num_lenguajes)
    
    heatmap_data = heatmap_data.drop('promedio', axis=1)
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='RdYlGn',
        text=np.round(heatmap_data.values, 2),
        texttemplate='%{text}%',
        textfont={"size": 10},
        colorbar=dict(title="Porcentaje<br>PR (%)")
    ))
    
    # Texto del título según cantidad de lenguajes
    if num_lenguajes == 15:
        subtitulo = "15 Lenguajes Seleccionados"
    elif num_lenguajes == 10:
        subtitulo = "Top 10 Lenguajes"
    else:
        subtitulo = "Top 5 Lenguajes"
    
    fig.update_layout(
        title={
            'text': f'Heatmap: Porcentaje de Pull Requests - {titulo_anio}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis_title='Período (Quarter)' if anio_seleccionado != 'Todos' else 'Período (Año-Quarter)',
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

def crear_medidores_promedio(anio_seleccionado='Todos'):
    """
    ¿Cuál es el promedio general de pull requests para cada uno de los 
    lenguajes de programación en el periodo de estudio 2020-2024?
    """

    if anio_seleccionado == 'Todos':
        df_filtered = df.copy()
        texto_periodo = "2020-2024"
    else:
        df_filtered = df[df['Año'] == int(anio_seleccionado)].copy()
        texto_periodo = anio_seleccionado
    
    # Calcular promedio por lenguaje (top 10)
    promedio_df = df_filtered.groupby('Lenguaje')['Porcentaje'].mean().reset_index()
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
            'text': (
                'Promedio General de Pull Requests por Lenguaje (2020-2024)'
                '<br><sub>(Este gráfico se actualiza automáticamente según el año seleccionado arriba)</sub><br>'
            ),
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        height=600,
        showlegend=False,
        paper_bgcolor='white',
        font=dict(size=10),
        margin=dict(t=120, b=40, l=40, r=40) 
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
            'Fuente: Madnight GitHub Hut | Enfoque: 15 Lenguajes Principales',
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
            # Contenedor del selector
            # Contenedor de los DOS selectores
            html.Div(style={
                'marginBottom': '20px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'gap': '30px',
                'flexWrap': 'wrap'
            }, children=[
                # Selector de Año
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}, children=[
                    html.Label(
                        'Año:',
                        style={
                            'fontSize': '16px',
                            'fontWeight': 'bold',
                            'color': colors['text']
                        }
                    ),
                    dcc.Dropdown(
                        id='dropdown-anio',
                        options=[
                            {'label': '2020-2024', 'value': 'Todos'},
                            {'label': '2020', 'value': '2020'},
                            {'label': '2021', 'value': '2021'},
                            {'label': '2022', 'value': '2022'},
                            {'label': '2023', 'value': '2023'},
                            {'label': '2024', 'value': '2024'}
                        ],
                        value='Todos',
                        clearable=False,
                        style={
                            'width': '200px',
                            'fontSize': '14px'
                        }
                    )
                ]),
                
                # Selector de Cantidad de Lenguajes (NUEVO)
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}, children=[
                    html.Label(
                        'Mostrar:',
                        style={
                            'fontSize': '16px',
                            'fontWeight': 'bold',
                            'color': colors['text']
                        }
                    ),
                    dcc.Dropdown(
                        id='dropdown-num-lenguajes',
                        options=[
                            {'label': 'Top 5 Lenguajes', 'value': 5},
                            {'label': 'Top 10 Lenguajes', 'value': 10},
                            {'label': 'Todos (15)', 'value': 15}
                        ],
                        value=15,
                        clearable=False,
                        style={
                            'width': '200px',
                            'fontSize': '14px'
                        }
                    )
                ])
            ]),
            
            # Gráfico que se actualizará con AMBOS filtros
            dcc.Graph(
                id='heatmap-quarters',
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
                # figure=crear_medidores_promedio(),
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
# CALLBACKS PARA INTERACTIVIDAD
# ============================================================================

@app.callback(
    Output('heatmap-quarters', 'figure'),
    [Input('dropdown-anio', 'value'),
     Input('dropdown-num-lenguajes', 'value')]
)
def actualizar_heatmap(anio_seleccionado, num_lenguajes):
    """
    Callback que actualiza el heatmap cuando se selecciona un año diferente
    """
    return crear_heatmap_quarters(anio_seleccionado, num_lenguajes)

@app.callback(
    Output('medidores-promedio', 'figure'),
    Input('dropdown-anio', 'value')
)
def actualizar_medidores(anio_seleccionado):
    """
    Callback que actualiza los medidores cuando se selecciona un año diferente
    Sincronizado con el filtro del Heatmap
    """
    return crear_medidores_promedio(anio_seleccionado)



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