import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output
import numpy as np
from plotly.subplots import make_subplots

# =========================
# 1) Cargar y preparar datos
# =========================

# Datos de Series de Tiempo y Rating Promedio
rating_promedio_df = pd.read_csv("Datos_procesados/Rating_promedio.csv")
time_series_df = pd.read_csv("Datos/Series_de_Tiempo.csv")
time_series_df['Date'] = pd.to_datetime(time_series_df['Date'])

# Datos de GitHub Trending
df_stats_lang = pd.read_csv('Datos_procesados/Estadisticas_lenguajes.csv')
df_top_repos = pd.read_csv('Datos_procesados/Top_repos_clean.csv')
df_repos_lang = pd.read_csv('Datos_procesados/Repos_por_lenguaje_clean.csv')

# Datos de Pull Requests
df_original = pd.read_csv('Datos_procesados/MadnightPullRequests_cleaned.csv')

# Filtro de lenguajes específicos para Pull Requests
LENGUAJES_SELECCIONADOS = [
    'Python', 'C', 'C++', 'C#', 'Java', 'JavaScript',
    'Assembly', 'R', 'Perl', 'Fortran', 'Rust',
    'MATLAB', 'PHP', 'Go', 'Kotlin'
]

df = df_original[df_original['Lenguaje'].isin(LENGUAJES_SELECCIONADOS)].copy()


# ============================================================================
# SECCIÓN 1: FUNCIONES PARA ANÁLISIS DE SERIES DE TIEMPO Y POPULARIDAD
# ============================================================================

def getIndicadorAnio(df, anio1='2024', anio2='2025'):
    """
    ¿Cuál fue el porcentaje de aumento o disminución en la popularidad
    de cada lenguaje de programación en el periodo seleccionado?
    """
    df_anio = df[['Language', anio1, anio2]].copy()
    df_anio['Indicador'] = (df_anio[anio2] - df_anio[anio1]).round(2)

    table = dash_table.DataTable(
        columns=[
            {"name": "Lenguaje", "id": "Language"},
            {"name": anio1, "id": anio1, "type": "numeric"},
            {"name": anio2, "id": anio2, "type": "numeric"},
            {"name": "Indicador (%)", "id": "Indicador", "type": "numeric"},
        ],
        data=df_anio.to_dict("records"),
        sort_action="native",
        sort_mode="single",
        style_table={
            "overflowX": "auto",
            "border": "1px solid #c6dbef",
            "borderRadius": "8px"
        },
        style_cell={
            "padding": "12px 15px",
            "fontFamily": "Segoe UI, Arial, sans-serif",
            "fontSize": "14px",
            "textAlign": "left",
            "border": "1px solid #deebf7",
            "color": "#08306b"
        },
        style_header={
            "backgroundColor": "#4292c6",
            "color": "white",
            "fontWeight": "bold",
            "border": "1px solid #2171b5",
            "textAlign": "center",
            "fontSize": "15px",
            "padding": "12px"
        },
        style_data={
            "backgroundColor": "white",
            "border": "1px solid #deebf7"
        },
        style_data_conditional=[
            # Filas alternas con fondo azul muy claro
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f7fbff"
            },
            # Indicador positivo - azul claro
            {
                "if": {
                    "filter_query": "{Indicador} > 0",
                    "column_id": "Indicador",
                },
                "backgroundColor": "#c6dbef",
                "color": "#084594",
                "fontWeight": "bold",
            },
            # Indicador negativo - rojo suave que combina
            {
                "if": {
                    "filter_query": "{Indicador} < 0",
                    "column_id": "Indicador",
                },
                "backgroundColor": "#fee5d9",
                "color": "#a50f15",
                "fontWeight": "bold",
            },
            # Indicador neutro (0)
            {
                "if": {
                    "filter_query": "{Indicador} = 0",
                    "column_id": "Indicador",
                },
                "backgroundColor": "#f0f0f0",
                "color": "#636363",
                "fontWeight": "bold",
            },
        ],
    )

    return table

def create_line_chart(df, anio1=2020, anio2=2025):
    """
    ¿Cómo ha sido el histórico de popularidad de cada uno de los lenguajes
    de programación seleccionados a lo largo del tiempo?
    """
    # Filtrar datos por rango de años
    df_filtered = df[(df['Year'] >= anio1) & (df['Year'] <= anio2)].copy()

    fig = px.line(
        df_filtered,
        x='Date',
        y='Rating',
        color='Language',
        title=f'Tendencia de Popularidad de Lenguajes de Programación ({anio1}-{anio2})',
        color_discrete_sequence=px.colors.qualitative.Light24,
        markers=True
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(b=100),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def get_monthly_winners(df, year1=2020, year2=2025):
    """
    ¿Cuál es el lenguaje de programación con más apariciones en el Top 1
    a lo largo de todos los años registrados?
    """
    df_filtered = df[(df['Year'] >= int(year1)) & (df['Year'] <= int(year2))].copy()
    df_filtered['Month'] = df_filtered["Date"].dt.strftime("%B")
    idx = df_filtered.groupby(["Year", "Month"])["Rating"].idxmax().reset_index(drop=True)
    winners = df_filtered.loc[idx, ["Year", "Month", "Language"]].copy()
    counts = (
        winners.groupby(["Language"])
        .size()
        .reset_index(name="Top1_Count").sort_values(by="Top1_Count", ascending=False)
    )
    fig = px.bar(
        counts,
        x='Language',
        y='Top1_Count',
        title=f'Número de Veces que Cada Lenguaje Fue el Mejor Calificado ({year1}-{year2})',
        color='Top1_Count',
        color_continuous_scale='blues',
        text_auto=True
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# ============================================================================
# SECCIÓN 2: FUNCIONES PARA GITHUB TRENDING
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
        textposition='inside',
        marker=dict(
            color=top_10['Promedio_Stars'],
            colorscale='blues',
            showscale=False,
            colorbar=dict(title="Estrellas<br>Promedio")
        ),
        hovertemplate='<b>%{x}</b><br>' +
                      'Promedio de Estrellas: %{y:,.0f}<br>' +
                      '<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': '<b>Promedio de Estrellas por Lenguaje</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#08306b'}
        },
        xaxis_title='Lenguaje de Programación',
        yaxis_title='Promedio de Estrellas',
        height=450,
        plot_bgcolor='rgba(247, 251, 255, 0.5)',
        paper_bgcolor='white',
        font=dict(size=12, color='#08306b'),
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
            colorscale='blues',
            showscale=False,
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
            'text': '<b>Top 10 Repositorios Más Populares (GitHub Trending)</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#08306b'}
        },
        xaxis_title='Número de Estrellas',
        yaxis_title='Repositorio',
        height=550,
        plot_bgcolor='rgba(247, 251, 255, 0.5)',
        paper_bgcolor='white',
        font=dict(size=11, color='#08306b'),
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
        marker=dict(color='#4292c6'),  # Azul medio de la paleta Blues
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
        marker=dict(color='#9ecae1'),  # Azul claro secundario de la paleta Blues
        hovertemplate='<b>%{x}</b><br>' +
                      'Forks: %{y:,}<br>' +
                      '<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': f'<b>Top 5 Repositorios de {lenguaje_inicial}</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#08306b'}
        },
        xaxis_title='Repositorio',
        yaxis_title='Cantidad',
        height=450,
        plot_bgcolor='rgba(247, 251, 255, 0.5)',
        paper_bgcolor='white',
        font=dict(size=11, color='#08306b'),
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
# SECCIÓN 3: FUNCIONES PARA PULL REQUESTS
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
            colorscale='blues',
            showscale=False,
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
            'text': '<b>Lenguajes con Más Pull Requests en el Top 1 (2020-2024)</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#08306b'}
        },
        xaxis_title='Conteo-Años en Top 1',
        yaxis_title='Lenguaje de Programación',
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['1-2020', '2-2021', '3-2022', '4-2023', '5-2024']
        ),
        height=400,
        plot_bgcolor='rgba(247, 251, 255, 0.5)',
        paper_bgcolor='white',
        font=dict(size=12, color='#08306b'),
        hovermode='closest',
        margin=dict(l=100, r=50, t=80, b=50)
    )

    max_count = top1_count['Años_en_Top1'].max()
    fig.add_vline(x=max_count, line_dash="dash", line_color="#2171b5",
                  annotation_text=f"Máximo: {max_count}",
                  annotation_position="top right",
                  annotation_font_color="#084594")

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
        colorscale='blues',
        text=np.round(heatmap_data.values, 2),
        texttemplate='%{text}%',
        textfont={"size": 11},
        colorbar=dict(title="Porcentaje<br>PR (%)")
    ))

    # Altura dinámica sincronizada con los medidores
    if num_lenguajes <= 5:
        altura = 400
    elif num_lenguajes <= 10:
        altura = 700
    else:
        altura = 1000

    fig.update_layout(
        title={
            'text': f'<b>Heatmap: Porcentaje de Pull Requests - {titulo_anio}</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#08306b'}
        },
        xaxis_title='Período (Quarter)' if anio_seleccionado != 'Todos' else 'Período (Año-Quarter)',
        yaxis_title='Lenguaje de Programación',
        height=altura,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis={'side': 'bottom'},
        font=dict(size=11, color='#08306b')
    )

    return fig

def crear_medidores_promedio(anio_seleccionado='Todos', num_lenguajes=10):
    """
    ¿Cuál es el promedio general de pull requests?
    """
    if anio_seleccionado == 'Todos':
        df_filtered = df.copy()
        titulo_grafico = "<b>Promedio General de Pull Requests por Lenguaje (2020-2024)</b>"
    else:
        df_filtered = df[df['Año'] == int(anio_seleccionado)].copy()
        titulo_grafico = f"<b>Promedio General de Pull Requests por Lenguaje ({anio_seleccionado})</b>"

    promedio_df = df_filtered.groupby('Lenguaje')['Porcentaje'].mean().reset_index()
    promedio_df = promedio_df.sort_values('Porcentaje', ascending=False).head(num_lenguajes)

    max_val = promedio_df['Porcentaje'].max() * 1.2

    # Calcular filas y columnas dinámicamente
    if num_lenguajes <= 5:
        n_cols = num_lenguajes
        n_rows = 1
    else:
        n_cols = 5
        n_rows = (num_lenguajes + 4) // 5  # Redondeo hacia arriba

    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        specs=[[{'type': 'indicator'}] * n_cols for _ in range(n_rows)],
        subplot_titles=promedio_df['Lenguaje'].tolist()
    )

    for idx, (_, row) in enumerate(promedio_df.iterrows(), 1):
        row_num = (idx - 1) // n_cols + 1
        col_num = (idx - 1) % n_cols + 1

        # Colores de la paleta Blues según el porcentaje
        if row['Porcentaje'] > 10:
            color = "#084594"  # Azul muy oscuro (alto)
        elif row['Porcentaje'] > 5:
            color = "#2171b5"  # Azul oscuro (medio)
        else:
            color = "#4292c6"  # Azul medio (bajo)

        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=row['Porcentaje'],
                number={'suffix': "%", 'font': {'size': 22, 'color': '#08306b'}},
                delta={
                    'reference': promedio_df['Porcentaje'].mean(),
                    'increasing': {'color': '#084594'},
                    'decreasing': {'color': '#9ecae1'}
                },
                gauge={
                    'axis': {
                        'range': [None, max_val],
                        'tickwidth': 1,
                        'tickcolor': "#c6dbef",
                        'tickfont': {'color': '#08306b', 'size': 10}
                    },
                    'bar': {'color': color, 'thickness': 0.75},
                    'bgcolor': "#f7fbff",
                    'borderwidth': 2,
                    'bordercolor': "#c6dbef",
                    'steps': [
                        {'range': [0, max_val * 0.33], 'color': '#f7fbff'},      # Azul muy claro
                        {'range': [max_val * 0.33, max_val * 0.66], 'color': '#deebf7'},  # Azul claro
                        {'range': [max_val * 0.66, max_val], 'color': '#c6dbef'}   # Azul medio-claro
                    ],
                    'threshold': {
                        'line': {'color': "#2171b5", 'width': 3},
                        'thickness': 0.75,
                        'value': promedio_df['Porcentaje'].mean()
                    }
                }
            ),
            row=row_num, col=col_num
        )

    # Altura dinámica sincronizada con el heatmap
    if num_lenguajes <= 5:
        altura = 400
    elif num_lenguajes <= 10:
        altura = 700
    else:
        altura = 1000

    fig.update_layout(
        title={
            'text': (
                f'{titulo_grafico}'
            ),
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#08306b'}
        },
        height=altura,
        showlegend=False,
        paper_bgcolor='white',
        font=dict(size=11, color='#08306b'),
        margin=dict(t=120, b=40, l=40, r=40)
    )

    return fig


# ============================================================================
# CREACIÓN DEL DASHBOARD
# ============================================================================

app = Dash(__name__)
app.title = "Dashboard Unificado - Análisis de Tendencias y Popularidad de Lenguajes"

#  ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#084594', '#08306b']
# https://plotly.com/python/colorscales/
colors = {
    'background_solid': '#f7fbff',        # Azul muy claro para el fondo
    'text': '#08306b',                     # Azul muy oscuro para el texto
    'text_light': '#2171b5',               # Azul oscuro para texto secundario
    'card': '#ffffff',                     # Blanco puro para las cards
    'accent': '#4292c6',                   # Azul medio-oscuro principal
    'accent_dark': '#2171b5',              # Azul oscuro
    'accent_light': '#6baed6',             # Azul medio-claro
    'secondary': '#9ecae1',                # Azul medio-claro secundario
    'gradient_primary': 'linear-gradient(135deg, #2171b5 0%, #084594 100%)',      # Gradiente azul oscuro
    'gradient_secondary': 'linear-gradient(135deg, #4292c6 0%, #2171b5 100%)',    # Gradiente azul medio
    'gradient_light': 'linear-gradient(135deg, #6baed6 0%, #4292c6 100%)',        # Gradiente azul claro
    'shadow': '0 10px 30px rgba(66, 146, 198, 0.15)',                             # Sombra azul suave
    'shadow_strong': '0 4px 20px rgba(33, 113, 181, 0.3)',                        # Sombra azul más fuerte
    'border_light': '#c6dbef',             # Borde azul claro
    'hover': '#deebf7'                     # Hover azul muy claro
}

style_user_dict = { 
    'display': 'block',
    'color': 'white',
    'textDecoration': 'none',
    'padding': '8px 0',
    'fontSize': '14px',
    'transition': 'color 0.3s'
    }
# Lista de años disponibles
years = ['2020', '2021', '2022', '2023', '2024', '2025']

# Preparar datos iniciales
fig_dropdown, lista_lenguajes = crear_dropdown_repos_por_lenguaje()

# ============================================================================
# LAYOUT DEL DASHBOARD
# ============================================================================

app.layout = html.Div(style={'background': colors['background_solid'], 'fontFamily': 'Segoe UI, Arial, sans-serif', 'minHeight': '100vh'}, children=[

    # ====================================================================
    # HEADER PRINCIPAL DEL DASHBOARD
    # ====================================================================
    html.Div(style={
        'background': colors['gradient_primary'],
        'padding': '50px 30px',
        'marginBottom': '40px',
        'boxShadow': colors['shadow_strong'],
        'borderBottom': f"4px solid {colors['accent_light']}"
    }, children=[
        html.H1(
            'Dashboard - Análisis de Lenguajes de Programación',
            style={
                'color': 'white',
                'textAlign': 'center',
                'margin': '0',
                'fontSize': '40px',
                'fontWeight': '700',
                'textShadow': '2px 2px 4px rgba(0,0,0,0.2)'
            }
        ),
        html.P(
            'Tendencias Históricas | Repositorios GitHub | Pull Requests',
            style={
                'color': 'white',
                'textAlign': 'center',
                'margin': '15px 0 0 0',
                'fontSize': '18px',
                'opacity': '0.95',
                'fontWeight': '400'
            }
        ),
        html.P(
            'Período 2020-2025',
            style={
                'color': colors['accent_light'],
                'textAlign': 'center',
                'margin': '10px 0 0 0',
                'fontSize': '16px',
                'fontWeight': '500'
            }
        )
    ]),

    # Contenedor principal
    html.Div(style={'maxWidth': '1900px', 'margin': '0 auto', 'padding': '20px'}, children=[

        # ====================================================================
        # SECCIÓN 1: ANÁLISIS DE POPULARIDAD Y SERIES DE TIEMPO
        # ====================================================================
        html.Div(style={
            'marginBottom': '50px'
        }, children=[

            # Título de la sección
            html.Div(style={
                'background': colors['gradient_secondary'],
                'padding': '20px 30px',
                'marginBottom': '30px',
                'borderRadius': '12px',
                'boxShadow': colors['shadow']
            }, children=[
                html.H2(
                    'Análisis de Popularidad y Tendencias Históricas',
                    style={
                        'color': 'white',
                        'textAlign': 'center',
                        'margin': '0',
                        'fontSize': '26px',
                        'fontWeight': '600'
                    }
                )
            ]),

            # Contenido de la sección
            html.Div(style={
                'display': 'flex',
                'gap': '20px'
            }, children=[

                # Columna izquierda: Tabla con dropdowns
                html.Div(children=[
                    # Filtros de años
                    html.Div(children=[
                        html.Div(children=[
                            html.Label("Año 1:", style={"fontWeight": "bold", "marginBottom": "5px", "color": colors['text']}),
                            dcc.Dropdown(
                                id='year-dropdown-1',
                                options=[{'label': year, 'value': year} for year in years],
                                value='2024',
                                clearable=False,
                                style={"width": "150px"}
                            ),
                        ], style={"marginRight": "20px"}),
                        html.Div(children=[
                            html.Label("Año 2:", style={"fontWeight": "bold", "marginBottom": "5px", "color": colors['text']}),
                            dcc.Dropdown(
                                id='year-dropdown-2',
                                options=[{'label': year, 'value': year} for year in years],
                                value='2025',
                                clearable=False,
                                style={"width": "150px"}
                            ),
                        ]),
                    ], style={
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "flex-end",
                        "marginBottom": "20px",
                        "gap": "20px"
                    }),
                    # Tabla
                    html.Div(
                        id='tabla-container',
                        children=[getIndicadorAnio(rating_promedio_df, '2024', '2025')]
                    )
                ], style={
                    "flex": "1",
                    "padding": "20px",
                    "backgroundColor": colors['card'],
                    "borderRadius": "12px",
                    "boxShadow": colors['shadow'], "border": f"1px solid {colors['border_light']}",
                    "marginRight": "10px"
                }),

                # Columna derecha: Serie de tiempo con filtro
                html.Div(children=[
                    # Filtro de rango de años
                    html.Div(children=[
                        html.Label("Rango de Años:", style={"fontWeight": "bold", "marginBottom": "10px", "textAlign": "center", "color": colors['text']}),
                        dcc.RangeSlider(
                            id='year-range-slider',
                            min=2020,
                            max=2025,
                            step=1,
                            marks={year: str(year) for year in range(2020, 2026)},
                            value=[2020, 2025],
                            tooltip={"placement": "bottom", "always_visible": False}
                        ),
                    ], style={
                        "padding": "20px",
                        "marginBottom": "20px"
                    }),
                    # Gráfico de serie de tiempo
                    html.Div(
                        id='timeseries-container',
                        children=[dcc.Graph(figure=create_line_chart(time_series_df, 2020, 2025))],
                        style={"marginBottom": "20px"}
                    ),
                    # Gráfico de ganadores mensuales
                    html.Div(
                        id='winners-container',
                        children=[dcc.Graph(figure=get_monthly_winners(time_series_df, 2020, 2025))]
                    )
                ], style={
                    "flex": "1",
                    "padding": "20px",
                    "backgroundColor": colors['card'],
                    "borderRadius": "12px",
                    "boxShadow": colors['shadow'], "border": f"1px solid {colors['border_light']}",
                    "marginLeft": "10px"
                })
            ])
        ]),

        # ====================================================================
        # SECCIÓN 2: ACTIVIDAD EN REPOSITORIOS (GITHUB TRENDING)
        # ====================================================================
        html.Div(style={
            'marginBottom': '50px'
        }, children=[

            # Título de la sección
            html.Div(style={
                'background': colors['gradient_secondary'],
                'padding': '20px 30px',
                'marginBottom': '30px',
                'borderRadius': '12px',
                'boxShadow': colors['shadow']
            }, children=[
                html.H2(
                    'Actividad en Repositorios (GitHub Trending)',
                    style={
                        'color': 'white',
                        'textAlign': 'center',
                        'margin': '0',
                        'fontSize': '26px',
                        'fontWeight': '600'
                    }
                )
            ]),

            # Gráficos 1 y 2: Promedio de Estrellas y Top Repositorios
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
                    'borderRadius': '12px',
                    'boxShadow': colors['shadow']
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
                    'borderRadius': '12px',
                    'boxShadow': colors['shadow']
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
                'borderRadius': '12px',
                'boxShadow': colors['shadow']
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
        # SECCIÓN 3: ANÁLISIS DE PULL REQUESTS
        # ====================================================================
        html.Div(children=[

            # Título de la sección
            html.Div(style={
                'background': colors['gradient_secondary'],
                'padding': '20px 30px',
                'marginBottom': '30px',
                'borderRadius': '12px',
                'boxShadow': colors['shadow']
            }, children=[
                html.H2(
                    'Análisis de Pull Requests en GitHub',
                    style={
                        'color': 'white',
                        'textAlign': 'center',
                        'margin': '0',
                        'fontSize': '26px',
                        'fontWeight': '600'
                    }
                )
            ]),
            # Pregunta 1: Gráfico de Barras Top
            html.Div(style={
                'backgroundColor': colors['card'],
                'padding': '25px',
                'marginBottom': '30px',
                'borderRadius': '12px',
                'boxShadow': colors['shadow']
            }, children=[
                dcc.Graph(
                    id='grafico-top-lenguajes',
                    figure=crear_grafico_top_lenguajes(),
                    config={'displayModeBar': False}
                )
            ]),

            # Contenedor principal: Dropdowns + Gráficos
            html.Div(style={
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '20px',
                'marginBottom': '30px'
            }, children=[
                # Fila 1: Dropdowns centrados
                html.Div(style={
                    'backgroundColor': colors['card'],
                    'padding': '20px',
                    'borderRadius': '12px',
                    'boxShadow': colors['shadow'],
                    'display': 'flex',
                    'justifyContent': 'center',
                    'alignItems': 'center',
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

                # Fila 2: Dos gráficos lado a lado (50% cada uno)
                html.Div(style={
                    'display': 'flex',
                    'flexDirection': 'row',
                    'gap': '20px',
                    'width': '100%',
                    'alignItems': 'stretch'
                }, children=[
                    # Gráfico Heatmap
                    html.Div(style={
                        'width': '50%',
                        'backgroundColor': colors['card'],
                        'padding': '25px',
                        'borderRadius': '12px',
                        'boxShadow': colors['shadow'],
                        'boxSizing': 'border-box',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center'
                    }, children=[
                        dcc.Graph(
                            id='heatmap-quarters',
                            config={'displayModeBar': False},
                            style={'height': '100%'}
                        )
                    ]),

                    # Gráfico Medidores
                    html.Div(style={
                        'width': '50%',
                        'backgroundColor': colors['card'],
                        'padding': '25px',
                        'borderRadius': '12px',
                        'boxShadow': colors['shadow'],
                        'boxSizing': 'border-box',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center'
                    }, children=[
                        dcc.Graph(
                            id='medidores-promedio',
                            config={'displayModeBar': False},
                            style={'height': '100%'}
                        )
                    ])
                ])
            ])
        ]),

        # ====================================================================
        # FOOTER
        # ====================================================================
        html.Div(style={
            'background': colors['gradient_primary'],
            'padding': '40px 20px',
            'marginTop': '50px',
            'color': 'white',
            'boxShadow': '0 -4px 20px rgba(102, 126, 234, 0.2)'
        }, children=[
            # Contenedor principal del footer
            html.Div(style={
                'maxWidth': '1400px',
                'margin': '0 auto',
                'display': 'flex',
                'justifyContent': 'space-between',
                'flexWrap': 'wrap',
                'gap': '40px'
            }, children=[
                # Columna izquierda: Integrantes del equipo
                html.Div(style={
                    'flex': '1',
                    'minWidth': '300px'
                }, children=[
                    html.H3('Integrantes del Equipo', style={
                        'marginBottom': '15px',
                        'fontSize': '19px',
                        'color': '#c6dbef',
                        'fontWeight': '600',
                        'letterSpacing': '0.5px'
                    }),
                    html.Div([
                        html.A('🔗 Angelo Zurita',
                            href='https://github.com/aszurita',
                            target='_blank',
                            style=style_user_dict),
                        html.A('🔗 José Marin',
                            href='https://github.com/JoseM0lina',
                            target='_blank',
                            style=style_user_dict),
                        html.A('🔗 Dhamar Quishpe Rivera',
                            href='https://github.com/dquishpe',
                            target='_blank',
                            style=style_user_dict)
                    ])
                ]),

                # Columna derecha: Sobre el Dashboard
                html.Div(style={
                    'flex': '1',
                    'minWidth': '300px'
                }, children=[
                    html.H3('Sobre el Dashboard', style={
                        'marginBottom': '15px',
                        'fontSize': '19px',
                        'color': '#c6dbef',
                        'fontWeight': '600',
                        'letterSpacing': '0.5px'
                    }),
                    html.P(
                        'Dashboard interactivo que analiza tendencias de lenguajes de programación '
                        'mediante datos de popularidad histórica, actividad en repositorios de GitHub '
                        'y análisis de Pull Requests del período 2020-2025.',
                        style={
                            'fontSize': '14px',
                            'lineHeight': '1.6',
                            'margin': '0'
                        }
                    )
                ])
            ]),

            # Línea divisoria
            html.Hr(style={
                'border': 'none',
                'borderTop': '1px solid rgba(255,255,255,0.1)',
                'margin': '30px 0 20px 0'
            }),

            # Copyright
            html.Div(style={
                'textAlign': 'center',
                'fontSize': '12px',
                'opacity': '0.7'
            }, children=[
                html.P('© 2025 | Proyecto de Análisis de Datos | Grupo 12', style={'margin': '0'}),
                html.P('Tecnología: Python • Dash • Plotly • Pandas', style={'margin': '5px 0 0 0'})
            ])
        ])
    ])
])

# ============================================================================
# CALLBACKS PARA INTERACTIVIDAD
# ============================================================================

# Callback para actualizar opciones del dropdown 1 basándose en la selección del dropdown 2
# El año 1 debe ser menor que el año 2
@app.callback(
    Output('year-dropdown-1', 'options'),
    Input('year-dropdown-2', 'value')
)
def update_dropdown1_options(selected_year2):
    """
    Actualiza las opciones del dropdown de año 1 para que solo muestre años menores al año 2
    """
    return [
        {'label': year, 'value': year, 'disabled': int(year) >= int(selected_year2)}
        for year in years
    ]

# Callback para actualizar opciones del dropdown 2 basándose en la selección del dropdown 1
# El año 2 debe ser mayor que el año 1
@app.callback(
    Output('year-dropdown-2', 'options'),
    Input('year-dropdown-1', 'value')
)
def update_dropdown2_options(selected_year1):
    """
    Actualiza las opciones del dropdown de año 2 para que solo muestre años mayores al año 1
    """
    return [
        {'label': year, 'value': year, 'disabled': int(year) <= int(selected_year1)}
        for year in years
    ]

# Callback para actualizar la tabla cuando cambian los años seleccionados
@app.callback(
    Output('tabla-container', 'children'),
    Input('year-dropdown-1', 'value'),
    Input('year-dropdown-2', 'value')
)
def update_table(year1, year2):
    """
    Actualiza la tabla de indicadores cuando se cambian los años seleccionados
    """
    if year1 and year2 and year1 != year2:
        return getIndicadorAnio(rating_promedio_df, year1, year2)
    return getIndicadorAnio(rating_promedio_df, '2024', '2025')

# Callback para actualizar el gráfico de serie de tiempo cuando cambia el rango
@app.callback(
    Output('timeseries-container', 'children'),
    Output('winners-container', 'children'),
    Input('year-range-slider', 'value')
)
def update_timeseries(year_range):
    """
    Actualiza los gráficos de serie de tiempo y ganadores mensuales cuando cambia el rango de años
    """
    if year_range and len(year_range) == 2:
        line_chart = dcc.Graph(figure=create_line_chart(time_series_df, year_range[0], year_range[1]))
        winners_chart = dcc.Graph(figure=get_monthly_winners(time_series_df, year_range[0], year_range[1]))
        return line_chart, winners_chart
    line_chart = dcc.Graph(figure=create_line_chart(time_series_df, 2020, 2025))
    winners_chart = dcc.Graph(figure=get_monthly_winners(time_series_df, 2020, 2025))
    return line_chart, winners_chart

# Callback para actualizar el gráfico de repositorios por lenguaje
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
        marker=dict(color='#4292c6'),  # Azul medio de la paleta Blues
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
        marker=dict(color='#9ecae1'),  # Azul claro secundario de la paleta Blues
        hovertemplate='<b>%{x}</b><br>' +
                      'Forks: %{y:,}<br>' +
                      '<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': f'<b>Top 5 Repositorios de {lenguaje_seleccionado}</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#08306b'}
        },
        xaxis_title='Repositorio',
        yaxis_title='Cantidad',
        height=450,
        plot_bgcolor='rgba(247, 251, 255, 0.5)',
        paper_bgcolor='white',
        font=dict(size=11, color='#08306b'),
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

# Callback para actualizar el heatmap
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

# Callback para actualizar los medidores
@app.callback(
    Output('medidores-promedio', 'figure'),
    [Input('dropdown-anio', 'value'),
     Input('dropdown-num-lenguajes', 'value')]
)
def actualizar_medidores(anio_seleccionado, num_lenguajes):
    """
    Callback que actualiza los medidores cuando se selecciona un año diferente
    o se cambia el número de lenguajes a mostrar
    """
    return crear_medidores_promedio(anio_seleccionado, num_lenguajes)


if __name__ == '__main__':
    app.run(debug=True, port=8050)
