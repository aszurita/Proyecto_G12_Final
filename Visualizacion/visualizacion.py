"""
Dashboard de Visualización - GitHub Trending & Pull Requests (2020-2024)
Trabajo Colaborativo - Análisis Completo
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import numpy as np
from plotly.subplots import make_subplots

print("Cargando datos...")

df_stats_lang = pd.read_csv('datos_procesados/estadisticas_lenguajes.csv')
df_top_repos = pd.read_csv('datos_procesados/top_repos_clean.csv')
df_repos_lang = pd.read_csv('datos_procesados/repos_por_lenguaje_clean.csv')
df_original = pd.read_csv('Datos_procesados/MadnightPullRequests_cleaned.csv')

# Filtro de lenguajes específicos para Pull Requests
LENGUAJES_SELECCIONADOS = [
    'Python', 'C', 'C++', 'C#', 'Java', 'JavaScript', 
    'Assembly', 'R', 'Perl', 'Fortran', 'Rust', 
    'MATLAB', 'PHP', 'Go', 'Kotlin'
]

df = df_original[df_original['Lenguaje'].isin(LENGUAJES_SELECCIONADOS)].copy()

print(f"✓ Datos cargados exitosamente")
print(f"  - GitHub Trending: {len(df_repos_lang)} repositorios")
print(f"  - Pull Requests: {len(df)} registros")

# ============================================================================
# SECCIÓN 1: GRÁFICOS DE GITHUB TRENDING
# ============================================================================

def crear_grafico_promedio_estrellas():
    """
    Gráfico 1: Promedio de Estrellas por Lenguaje
    """
    top_10 = df_stats_lang.nlargest(10, 'Promedio_Stars')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top_10['Language'],
        y=top_10['Promedio_Stars'],
        text=top_10['Promedio_Stars'].apply(lambda x: f'{x:,.0f}'),
        textposition='outside',
        marker=dict(
            color=top_10['Promedio_Stars'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Estrellas<br>Promedio")
        ),
        hovertemplate='<b>%{x}</b><br>' +
                      'Promedio de Estrellas: %{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Promedio de Estrellas por Lenguaje',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis_title='Lenguaje de Programación',
        yaxis_title='Promedio de Estrellas',
        height=450,
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        paper_bgcolor='white',
        font=dict(size=12),
        hovermode='closest',
        margin=dict(l=60, r=50, t=80, b=80)
    )
    
    return fig

def crear_grafico_top_repositorios():
    """
    Gráfico 2: Top 10 Repositorios Más Populares
    """
    top_repos = df_top_repos.nlargest(10, 'NumberOfStar').sort_values('NumberOfStar')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_repos['Repository'],
        x=top_repos['NumberOfStar'],
        orientation='h',
        text=top_repos['NumberOfStar'].apply(lambda x: f'{x:,}'),
        textposition='outside',
        marker=dict(
            color=top_repos['NumberOfStar'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Número de<br>Estrellas")
        ),
        customdata=np.column_stack((top_repos['Language'], top_repos['User'], top_repos['NumberOfFork'])),
        hovertemplate='<b>%{y}</b><br>' +
                      'Estrellas: %{x:,}<br>' +
                      'Lenguaje: %{customdata[0]}<br>' +
                      'Usuario: %{customdata[1]}<br>' +
                      'Forks: %{customdata[2]:,}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Top 10 Repositorios Más Populares (GitHub Trending)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis_title='Número de Estrellas',
        yaxis_title='Repositorio',
        height=550,
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        paper_bgcolor='white',
        font=dict(size=11),
        hovermode='closest',
        margin=dict(l=200, r=80, t=80, b=60)
    )
    
    return fig

def crear_dropdown_repos_por_lenguaje():
    """
    Gráfico 3: Top 5 Repositorios por Lenguaje con Estrellas y Forks
    """
    lenguajes = sorted(df_repos_lang['Language'].unique())
    lenguaje_inicial = 'Python'
    repos_inicial = df_repos_lang[df_repos_lang['Language'] == lenguaje_inicial].nlargest(5, 'NumberOfStar')
    
    fig = go.Figure()
    
    # Barra de Estrellas
    fig.add_trace(go.Bar(
        name='Estrellas',
        x=repos_inicial['Repository'],
        y=repos_inicial['NumberOfStar'],
        text=repos_inicial['NumberOfStar'].apply(lambda x: f'{x:,}'),
        textposition='outside',
        marker=dict(color='#3498db'),
        hovertemplate='<b>%{x}</b><br>' +
                      'Estrellas: %{y:,}<br>' +
                      '<extra></extra>'
    ))
    
    # Barra de Forks
    fig.add_trace(go.Bar(
        name='Forks',
        x=repos_inicial['Repository'],
        y=repos_inicial['NumberOfFork'],
        text=repos_inicial['NumberOfFork'].apply(lambda x: f'{x:,}'),
        textposition='outside',
        marker=dict(color='#95a5a6'),
        hovertemplate='<b>%{x}</b><br>' +
                      'Forks: %{y:,}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Top 5 Repositorios de {lenguaje_inicial}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis_title='Repositorio',
        yaxis_title='Cantidad',
        height=450,
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        paper_bgcolor='white',
        font=dict(size=11),
        hovermode='closest',
        margin=dict(l=60, r=50, t=80, b=100),
        xaxis={'tickangle': -45},
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig, lenguajes

# ============================================================================
# SECCIÓN 2: GRÁFICOS DE PULL REQUESTS
# ============================================================================

def crear_grafico_top_lenguajes():
    """
    ¿Cuál es el lenguaje de programación con más pull request en el Top 1?
    """
    top1_df = df[df['Ranking'] == 1].copy()
    
    top1_por_anio = (
        top1_df
        .groupby(['Año', 'Lenguaje'])
        .size()
        .reset_index(name='Veces_Top1_en_Anio')
    )

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
    
    max_count = top1_count['Años_en_Top1'].max()
    fig.add_vline(x=max_count, line_dash="dash", line_color="red", 
                  annotation_text=f"Máximo: {max_count}", 
                  annotation_position="top right")
    
    return fig


def crear_heatmap_quarters(anio_seleccionado='Todos', num_lenguajes=15):
    """
    ¿Cuál es el porcentaje de pull requests por trimestres?
    """
    if anio_seleccionado == 'Todos':
        df_filtered = df.copy()
        titulo_anio = "Todos los Años (2020-2024)"
    else:
        df_filtered = df[df['Año'] == int(anio_seleccionado)].copy()
        titulo_anio = f"Año {anio_seleccionado}"
    
    if anio_seleccionado == 'Todos':
        df_filtered['Periodo'] = df_filtered['Año'].astype(str) + '-Q' + df_filtered['Quarter'].astype(str)
    else:
        df_filtered['Periodo'] = 'Q' + df_filtered['Quarter'].astype(str)
    
    heatmap_data = df_filtered.pivot_table(
        index='Lenguaje',
        columns='Periodo',
        values='Porcentaje',
        aggfunc='mean'
    )
    
    heatmap_data = heatmap_data.fillna(0)

    if anio_seleccionado != 'Todos':
        quarter_order = ['Q1', 'Q2', 'Q3', 'Q4']
        heatmap_data = heatmap_data[[col for col in quarter_order if col in heatmap_data.columns]]
    
    heatmap_data['promedio'] = heatmap_data.mean(axis=1)
    heatmap_data = heatmap_data.sort_values('promedio', ascending=False)
    
    if num_lenguajes < 15:
        heatmap_data = heatmap_data.head(num_lenguajes)
    
    heatmap_data = heatmap_data.drop('promedio', axis=1)
    
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

def crear_medidores_promedio(anio_seleccionado='Todos'):
    """
    ¿Cuál es el promedio general de pull requests?
    """
    if anio_seleccionado == 'Todos':
        df_filtered = df.copy()
    else:
        df_filtered = df[df['Año'] == int(anio_seleccionado)].copy()
    
    promedio_df = df_filtered.groupby('Lenguaje')['Porcentaje'].mean().reset_index()
    promedio_df = promedio_df.sort_values('Porcentaje', ascending=False).head(10)
    
    max_val = promedio_df['Porcentaje'].max() * 1.2
    
    fig = make_subplots(
        rows=2, cols=5,
        specs=[[{'type': 'indicator'}] * 5] * 2,
        subplot_titles=promedio_df['Lenguaje'].tolist()
    )
    
    for idx, (_, row) in enumerate(promedio_df.iterrows(), 1):
        row_num = (idx - 1) // 5 + 1
        col_num = (idx - 1) % 5 + 1
        
        if row['Porcentaje'] > 10:
            color = "#27ae60"
        elif row['Porcentaje'] > 5:
            color = "#f39c12"
        else:
            color = "#e74c3c"
        
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

app = Dash(__name__)
app.title = "Dashboard - Análisis de Tendencias y Popularidad de Lenguajes"

colors = {
    'background': '#f5f7fa',
    'text': '#2c3e50',
    'card': '#ffffff',
    'accent': '#3498db'
}

fig_dropdown, lista_lenguajes = crear_dropdown_repos_por_lenguaje()

# ============================================================================
# LAYOUT DEL DASHBOARD
# ============================================================================

app.layout = html.Div(style={'backgroundColor': colors['background'], 'fontFamily': 'Arial, sans-serif'}, children=[
    
    # Header Principal
    html.Div(style={
        'backgroundColor': colors['accent'],
        'padding': '30px',
        'marginBottom': '30px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }, children=[
        html.H1(
            'Análisis de Tendencias y Popularidad de Lenguajes de Programación',
            style={
                'color': 'white',
                'textAlign': 'center',
                'margin': '0',
                'fontSize': '36px'
            }
        ),
        html.P(
            'Dashboard Interactivo | Período 2020-2024',
            style={
                'color': 'white',
                'textAlign': 'center',
                'margin': '10px 0 0 0',
                'fontSize': '16px',
                'opacity': '0.9'
            }
        )
    ]),
    
    # Contenedor principal
    html.Div(style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '20px'}, children=[
        
        # ====================================================================
        # SUBSECCIÓN 1: ACTIVIDAD EN REPOSITORIOS (GITHUB TRENDING)
        # ====================================================================
        
        html.Div(style={
            'marginBottom': '50px'
        }, children=[
            
            # Título de la subsección
            html.Div(style={
                'backgroundColor': '#3498db',
                'padding': '15px 25px',
                'marginBottom': '25px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 6px rgba(0,0,0,0.1)'
            }, children=[
                html.H1(
                    'Actividad en Repositorios (GitHub Trending)',
                    style={
                        'color': 'white',
                        'textAlign': 'center',
                        'margin': '0',
                        'fontSize': '36px'
                    }
                )
            ]),
            
            # Gráficos 1 y 2:
            html.Div(style={
                'display': 'grid',
                'gridTemplateColumns': '1fr 1fr',
                'gap': '25px',
                'marginBottom': '25px'
            }, children=[
                # Gráfico 1: Promedio de Estrellas
                html.Div(style={
                    'backgroundColor': colors['card'],
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
                }, children=[
                    dcc.Graph(
                        id='grafico-promedio-estrellas',
                        figure=crear_grafico_promedio_estrellas(),
                        config={'displayModeBar': False}
                    )
                ]),
                
                # Gráfico 2: Top Repositorios
                html.Div(style={
                    'backgroundColor': colors['card'],
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
                }, children=[
                    dcc.Graph(
                        id='grafico-top-repositorios',
                        figure=crear_grafico_top_repositorios(),
                        config={'displayModeBar': False}
                    )
                ])
            ]),
            
            # Gráfico 3: Dropdown Interactivo
            html.Div(style={
                'backgroundColor': colors['card'],
                'padding': '25px',
                'borderRadius': '10px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
            }, children=[
                html.Label(
                    'Seleccionar Lenguaje de Programación:',
                    style={
                        'fontSize': '14px',
                        'fontWeight': 'bold',
                        'marginBottom': '10px',
                        'display': 'block',
                        'color': colors['text']
                    }
                ),
                dcc.Dropdown(
                    id='dropdown-lenguaje',
                    options=[{'label': lang, 'value': lang} for lang in lista_lenguajes],
                    value='Python',
                    style={'marginBottom': '20px'}
                ),
                dcc.Graph(
                    id='grafico-repos-por-lenguaje',
                    figure=fig_dropdown,
                    config={'displayModeBar': False}
                )
            ])
        ]),
        
        # ====================================================================
        # SUBSECCIÓN 2: ANÁLISIS DE PULL REQUESTS
        # ====================================================================
        
        html.Div(children=[
            
            # Título de la sección
            html.Div(style={
                'backgroundColor': colors['accent'],
                'padding': '30px',
                'marginBottom': '30px',
                'borderRadius': '10px',
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
                html.Div(style={
                    'marginBottom': '20px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'gap': '30px',
                    'flexWrap': 'wrap'
                }, children=[
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
                dcc.Graph(
                    id='medidores-promedio',
                    config={'displayModeBar': False}
                )
            ])
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
    Output('grafico-repos-por-lenguaje', 'figure'),
    Input('dropdown-lenguaje', 'value')
)
def actualizar_grafico_lenguaje(lenguaje_seleccionado):
    """
    Actualiza el gráfico cuando se selecciona un lenguaje diferente
    """
    repos = df_repos_lang[df_repos_lang['Language'] == lenguaje_seleccionado].nlargest(5, 'NumberOfStar')
    
    fig = go.Figure()
    
    # Barra de Estrellas
    fig.add_trace(go.Bar(
        name='Estrellas',
        x=repos['Repository'],
        y=repos['NumberOfStar'],
        text=repos['NumberOfStar'].apply(lambda x: f'{x:,}'),
        textposition='outside',
        marker=dict(color='#3498db'),
        hovertemplate='<b>%{x}</b><br>' +
                      'Estrellas: %{y:,}<br>' +
                      '<extra></extra>'
    ))
    
    # Barra de Forks
    fig.add_trace(go.Bar(
        name='Forks',
        x=repos['Repository'],
        y=repos['NumberOfFork'],
        text=repos['NumberOfFork'].apply(lambda x: f'{x:,}'),
        textposition='outside',
        marker=dict(color='#95a5a6'),
        hovertemplate='<b>%{x}</b><br>' +
                      'Forks: %{y:,}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Top 5 Repositorios de {lenguaje_seleccionado}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis_title='Repositorio',
        yaxis_title='Cantidad',
        height=450,
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        paper_bgcolor='white',
        font=dict(size=11),
        hovermode='closest',
        margin=dict(l=60, r=50, t=80, b=100),
        xaxis={'tickangle': -45},
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

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
    print("DASHBOARD INICIADO")
    print(f"\nAccede al dashboard en: http://127.0.0.1:8050/")
    print(f"\nPresiona CTRL+C para detener el servidor\n")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8050)