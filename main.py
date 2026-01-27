import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import numpy as np
from plotly.subplots import make_subplots

# Importar agente IA (manejo de error si no esta configurado)
try:
    from ai_agent import CodeTrendsAgent
    AI_AVAILABLE = True
except Exception as e:
    AI_AVAILABLE = False
    print(f"Agente IA no disponible: {e}")

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

def getIndicadorAnio(df, anio1='2024', anio2='2025', selected_language=None):
    """
    ¿Cuál fue el porcentaje de aumento o disminución en la popularidad
    de cada lenguaje de programación en el periodo seleccionado?
    """
    df_anio = df[['Language', anio1, anio2]].copy()
    df_anio['Indicador'] = (df_anio[anio2] - df_anio[anio1]).round(2)
    df_anio = df_anio.sort_values(by="Indicador",ascending=False)

    # Estilos condicionales base
    style_data_conditional = [
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
    ]

    # Si hay un lenguaje seleccionado, resaltar esa fila y atenuar las demás
    if selected_language:
        style_data_conditional.append({
            "if": {
                "filter_query": f"{{Language}} = '{selected_language}'",
            },
            "backgroundColor": "#2171b5",
            "color": "white",
            "fontWeight": "bold",
        })
        # Atenuar las filas no seleccionadas
        for lang in df_anio['Language'].unique():
            if lang != selected_language:
                style_data_conditional.append({
                    "if": {
                        "filter_query": f"{{Language}} = '{lang}'",
                    },
                    "opacity": "0.4",
                })

    table = dash_table.DataTable(
        id='tabla-indicador',
        columns=[
            {"name": "Lenguaje", "id": "Language"},
            {"name": anio1, "id": anio1, "type": "numeric"},
            {"name": anio2, "id": anio2, "type": "numeric"},
            {"name": "Indicador (%)", "id": "Indicador", "type": "numeric"},
        ],
        data=df_anio.to_dict("records"),
        sort_action="native",
        sort_mode="single",
        row_selectable=False,
        cell_selectable=True,
        style_table={
            "overflowX": "auto",
            "border": "1px solid #c6dbef",
            "borderRadius": "8px",
            "cursor": "pointer"
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
        style_data_conditional=style_data_conditional,
    )

    return table

def create_line_chart(df, anio1=2020, anio2=2025, selected_language=None):
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

    # Si hay un lenguaje seleccionado, resaltar solo ese
    if selected_language:
        for trace in fig.data:
            if trace.name == selected_language:
                trace.line.width = 4
                trace.marker.size = 10
            else:
                trace.opacity = 0.2
                trace.line.width = 1

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=60, b=100),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 12, 'color': '#08306b'}
        }
    )

    return fig

def get_monthly_winners(df, year1=2020, year2=2025, selected_language=None):
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

    # Crear colores personalizados si hay un lenguaje seleccionado
    if selected_language:
        colors_list = []
        opacities = []
        for lang in counts['Language']:
            if lang == selected_language:
                colors_list.append('#084594')  # Azul oscuro para seleccionado
                opacities.append(1)
            else:
                colors_list.append('#c6dbef')  # Azul claro para no seleccionados
                opacities.append(0.3)

        fig = go.Figure(data=[go.Bar(
            x=counts['Language'],
            y=counts['Top1_Count'],
            text=counts['Top1_Count'],
            marker=dict(color=colors_list, opacity=opacities),
            textfont=dict(size=15, color='black', family='Arial Black'),
            textposition='outside'
        )])
        fig.update_layout(
            title=f'Número de Veces que Cada Lenguaje Fue el Mejor Calificado ({year1}-{year2})',
            xaxis_title='Language',
            yaxis_title='Top1_Count'
        )
    else:
        fig = px.bar(
            counts,
            x='Language',
            y='Top1_Count',
            title=f'Número de Veces que Cada Lenguaje Fue el Mejor Calificado ({year1}-{year2})',
            color='Top1_Count',
            color_continuous_scale='blues',
            text='Top1_Count'
        )
        fig.update_traces(
            textfont=dict(size=15, color='black', family='Arial Black'),
            textposition='outside'
        )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=40),
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#08306b'}
        }
    )
    return fig

# ============================================================================
# SECCIÓN 2: FUNCIONES PARA GITHUB TRENDING
# ============================================================================

def crear_grafico_promedio_estrellas(selected_language=None):
    """
    Gráfico 1: Promedio de Estrellas por Lenguaje
    """
    top_10 = df_stats_lang.nlargest(10, 'Promedio_Stars')

    # Crear colores y opacidades basados en selección
    if selected_language and selected_language in top_10['Language'].values:
        colors_list = ['#084594' if lang == selected_language else '#c6dbef' for lang in top_10['Language']]
        opacities = [1 if lang == selected_language else 0.3 for lang in top_10['Language']]
    else:
        colors_list = top_10['Promedio_Stars']
        opacities = [1] * len(top_10)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=top_10['Language'],
        y=top_10['Promedio_Stars'],
        text=top_10['Promedio_Stars'].apply(lambda x: f'{x:,.0f}'),
        textposition='inside',
        marker=dict(
            color=colors_list if selected_language else top_10['Promedio_Stars'],
            colorscale='blues' if not selected_language else None,
            showscale=False,
            opacity=opacities if selected_language else None
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

def crear_heatmap_quarters(anio_seleccionado='Todos', num_lenguajes=15, selected_language=None):
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

    # Crear colores personalizados si hay un lenguaje seleccionado
    if selected_language and selected_language in heatmap_data.index:
        # Crear una matriz de opacidades
        z_values = heatmap_data.values
        shapes = []

        for i, lang in enumerate(heatmap_data.index):
            if lang != selected_language:
                # Agregar un rectángulo semi-transparente sobre las filas no seleccionadas
                shapes.append(dict(
                    type="rect",
                    xref="x",
                    yref="y",
                    x0=-0.5,
                    x1=len(heatmap_data.columns) - 0.5,
                    y0=i - 0.5,
                    y1=i + 0.5,
                    fillcolor="rgba(255, 255, 255, 0.7)",
                    line=dict(width=0),
                    layer="above"
                ))

        fig = go.Figure(data=go.Heatmap(
            z=z_values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='blues',
            text=np.round(z_values, 2),
            texttemplate='%{text}%',
            textfont={"size": 11, "color": "black"},
            colorbar=dict(title="Porcentaje<br>PR (%)")
        ))
        fig.update_layout(shapes=shapes)
    else:
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='blues',
            text=np.round(heatmap_data.values, 2),
            texttemplate='%{text}%',
            textfont={"size": 11, "color": "black"},
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

def crear_medidores_promedio(anio_seleccionado='Todos', num_lenguajes=10, selected_language=None):
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

    # Crear títulos con estilo según selección
    subplot_titles = []
    for lang in promedio_df['Lenguaje'].tolist():
        if selected_language and lang == selected_language:
            subplot_titles.append(f"<b>{lang}</b>")
        elif selected_language:
            subplot_titles.append(f"<span style='opacity:0.3'>{lang}</span>")
        else:
            subplot_titles.append(lang)

    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        specs=[[{'type': 'indicator'}] * n_cols for _ in range(n_rows)],
        subplot_titles=subplot_titles
    )

    for idx, (_, row) in enumerate(promedio_df.iterrows(), 1):
        row_num = (idx - 1) // n_cols + 1
        col_num = (idx - 1) % n_cols + 1
        lang = row['Lenguaje']

        # Determinar si este indicador está seleccionado
        is_selected = (selected_language is None) or (lang == selected_language)

        # Colores de la paleta Blues según el porcentaje
        if row['Porcentaje'] > 10:
            color = "#084594"  # Azul muy oscuro (alto)
        elif row['Porcentaje'] > 5:
            color = "#2171b5"  # Azul oscuro (medio)
        else:
            color = "#4292c6"  # Azul medio (bajo)

        # Si no está seleccionado, usar colores más claros/opacos
        if not is_selected:
            color = "#deebf7"  # Color muy claro para no seleccionados
            number_color = '#c6dbef'
        else:
            number_color = '#08306b'

        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=row['Porcentaje'],
                number={'suffix': "%", 'font': {'size': 22, 'color': number_color}},
                delta={
                    'reference': promedio_df['Porcentaje'].mean(),
                    'increasing': {'color': '#084594' if is_selected else '#deebf7'},
                    'decreasing': {'color': '#9ecae1' if is_selected else '#f7fbff'}
                },
                gauge={
                    'axis': {
                        'range': [None, max_val],
                        'tickwidth': 1,
                        'tickcolor': "#c6dbef",
                        'tickfont': {'color': '#08306b' if is_selected else '#deebf7', 'size': 10}
                    },
                    'bar': {'color': color, 'thickness': 0.75},
                    'bgcolor': "#f7fbff",
                    'borderwidth': 2,
                    'bordercolor': "#c6dbef" if is_selected else "#f7fbff",
                    'steps': [
                        {'range': [0, max_val * 0.33], 'color': '#f7fbff'},
                        {'range': [max_val * 0.33, max_val * 0.66], 'color': '#deebf7' if is_selected else '#f7fbff'},
                        {'range': [max_val * 0.66, max_val], 'color': '#c6dbef' if is_selected else '#f7fbff'}
                    ],
                    'threshold': {
                        'line': {'color': "#2171b5" if is_selected else "#f7fbff", 'width': 3},
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

    # Store para guardar el lenguaje seleccionado (interactividad tipo Power BI)
    dcc.Store(id='selected-language-store', data=None),

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
                'flexDirection': 'column',
                'gap': '20px'
            }, children=[

                # Fila 1: Rango de años centrado
                html.Div(style={
                    "backgroundColor": colors['card'],
                    "borderRadius": "12px",
                    "boxShadow": colors['shadow'],
                    "border": f"1px solid {colors['border_light']}",
                    "padding": "20px 40px"
                }, children=[
                    html.Label("Rango de Años:", style={
                        "fontWeight": "bold",
                        "marginBottom": "15px",
                        "display": "block",
                        "textAlign": "center",
                        "color": colors['text'],
                        "fontSize": "16px"
                    }),
                    dcc.RangeSlider(
                        id='year-range-slider',
                        min=2020,
                        max=2025,
                        step=1,
                        marks={year: str(year) for year in range(2020, 2026)},
                        value=[2020, 2025],
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ]),

                # Fila 2: Tabla a la izquierda y gráficos a la derecha
                html.Div(style={
                    'display': 'flex',
                    'gap': '20px',
                    'alignItems': 'stretch'
                }, children=[

                    # Columna izquierda: Tabla
                    html.Div(style={
                        "flex": "1",
                        "padding": "20px",
                        "backgroundColor": colors['card'],
                        "borderRadius": "12px",
                        "boxShadow": colors['shadow'],
                        "border": f"1px solid {colors['border_light']}",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center"
                    }, children=[
                        html.Div(
                            id='tabla-container',
                            children=[getIndicadorAnio(rating_promedio_df, '2020', '2025')]
                        )
                    ]),

                    # Columna derecha: Gráficos
                    html.Div(style={
                        "flex": "1",
                        "padding": "20px",
                        "backgroundColor": colors['card'],
                        "borderRadius": "12px",
                        "boxShadow": colors['shadow'],
                        "border": f"1px solid {colors['border_light']}",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "space-between"
                    }, children=[
                        # Gráfico de serie de tiempo
                        html.Div(
                            id='timeseries-container',
                            children=[dcc.Graph(figure=create_line_chart(time_series_df, 2020, 2025))],
                            style={"flex": "1"}
                        ),
                        # Gráfico de ganadores mensuales
                        html.Div(
                            id='winners-container',
                            children=[dcc.Graph(figure=get_monthly_winners(time_series_df, 2020, 2025))],
                            style={"flex": "1"}
                        )
                    ])
                ])
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
        # SECCION 4: ASISTENTE IA CONVERSACIONAL
        # ====================================================================
        html.Div(style={
            'marginBottom': '50px'
        }, children=[
            # Titulo de la seccion
            html.Div(style={
                'background': colors['gradient_secondary'],
                'padding': '20px 30px',
                'marginBottom': '30px',
                'borderRadius': '12px',
                'boxShadow': colors['shadow']
            }, children=[
                html.H2(
                    'CodeTrends AI Assistant',
                    style={
                        'color': 'white',
                        'textAlign': 'center',
                        'margin': '0',
                        'fontSize': '26px',
                        'fontWeight': '600'
                    }
                )
            ]),

            # Contenedor del chat
            html.Div(style={
                'backgroundColor': colors['card'],
                'borderRadius': '12px',
                'boxShadow': colors['shadow'],
                'padding': '25px',
                'border': f"1px solid {colors['border_light']}"
            }, children=[
                # Descripcion
                html.P(
                    'Preguntame sobre lenguajes de programacion, tendencias, comparaciones o recomendaciones de carrera.',
                    style={
                        'color': colors['text_light'],
                        'textAlign': 'center',
                        'marginBottom': '20px',
                        'fontSize': '14px'
                    }
                ),

                # Preguntas rapidas sugeridas
                html.Div(style={
                    'display': 'flex',
                    'justifyContent': 'center',
                    'gap': '10px',
                    'flexWrap': 'wrap',
                    'marginBottom': '20px'
                }, children=[
                    html.Button(
                        'Mejor lenguaje 2025?',
                        id='quick-q1',
                        style={
                            'padding': '8px 16px',
                            'borderRadius': '20px',
                            'border': f"1px solid {colors['accent']}",
                            'backgroundColor': 'white',
                            'color': colors['accent'],
                            'cursor': 'pointer',
                            'fontSize': '12px'
                        }
                    ),
                    html.Button(
                        'Python vs JavaScript',
                        id='quick-q2',
                        style={
                            'padding': '8px 16px',
                            'borderRadius': '20px',
                            'border': f"1px solid {colors['accent']}",
                            'backgroundColor': 'white',
                            'color': colors['accent'],
                            'cursor': 'pointer',
                            'fontSize': '12px'
                        }
                    ),
                    html.Button(
                        'Lenguajes para IA',
                        id='quick-q3',
                        style={
                            'padding': '8px 16px',
                            'borderRadius': '20px',
                            'border': f"1px solid {colors['accent']}",
                            'backgroundColor': 'white',
                            'color': colors['accent'],
                            'cursor': 'pointer',
                            'fontSize': '12px'
                        }
                    ),
                    html.Button(
                        'Rust o Go?',
                        id='quick-q4',
                        style={
                            'padding': '8px 16px',
                            'borderRadius': '20px',
                            'border': f"1px solid {colors['accent']}",
                            'backgroundColor': 'white',
                            'color': colors['accent'],
                            'cursor': 'pointer',
                            'fontSize': '12px'
                        }
                    ),
                ]),

                # Area de historial del chat
                html.Div(
                    id='chat-history',
                    style={
                        'height': '400px',
                        'overflowY': 'auto',
                        'border': f"1px solid {colors['border_light']}",
                        'borderRadius': '8px',
                        'padding': '15px',
                        'marginBottom': '15px',
                        'backgroundColor': '#f7fbff'
                    },
                    children=[
                        html.Div([
                            html.Strong("CodeTrends AI: ", style={'color': colors['accent']}),
                            html.Span(
                                "Hola! Soy tu asistente de analisis de lenguajes de programacion. "
                                "Puedo ayudarte con tendencias, comparaciones y recomendaciones basadas en datos 2020-2025. "
                                "Que te gustaria saber?",
                                style={'color': colors['text']}
                            )
                        ], style={'marginBottom': '10px', 'padding': '10px', 'backgroundColor': 'white', 'borderRadius': '8px'})
                    ]
                ),

                # Input y boton de enviar
                html.Div(style={
                    'display': 'flex',
                    'gap': '10px'
                }, children=[
                    dcc.Input(
                        id='chat-input',
                        type='text',
                        placeholder='Escribe tu pregunta aqui...',
                        style={
                            'flex': '1',
                            'padding': '12px 15px',
                            'borderRadius': '8px',
                            'border': f"1px solid {colors['border_light']}",
                            'fontSize': '14px',
                            'outline': 'none'
                        },
                        debounce=True
                    ),
                    html.Button(
                        'Enviar',
                        id='send-button',
                        style={
                            'padding': '12px 25px',
                            'borderRadius': '8px',
                            'border': 'none',
                            'backgroundColor': colors['accent'],
                            'color': 'white',
                            'cursor': 'pointer',
                            'fontSize': '14px',
                            'fontWeight': 'bold'
                        }
                    ),
                    html.Button(
                        'Limpiar',
                        id='clear-button',
                        style={
                            'padding': '12px 20px',
                            'borderRadius': '8px',
                            'border': f"1px solid {colors['accent']}",
                            'backgroundColor': 'white',
                            'color': colors['accent'],
                            'cursor': 'pointer',
                            'fontSize': '14px'
                        }
                    )
                ]),

                # Estado de carga
                dcc.Loading(
                    id='loading-chat',
                    type='dots',
                    color=colors['accent'],
                    children=[html.Div(id='chat-loading-output')]
                ),

                # Store para el historial
                dcc.Store(id='chat-history-store', data=[])
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

# Callback para actualizar la tabla y gráficos cuando cambia el rango de años
@app.callback(
    Output('tabla-container', 'children'),
    Output('timeseries-container', 'children'),
    Output('winners-container', 'children'),
    Input('year-range-slider', 'value')
)
def update_section1(year_range):
    """
    Actualiza la tabla y los gráficos cuando cambia el rango de años
    """
    if year_range and len(year_range) == 2:
        year1, year2 = str(year_range[0]), str(year_range[1])
        tabla = getIndicadorAnio(rating_promedio_df, year1, year2)
        line_chart = dcc.Graph(figure=create_line_chart(time_series_df, year_range[0], year_range[1]))
        winners_chart = dcc.Graph(figure=get_monthly_winners(time_series_df, year_range[0], year_range[1]))
        return tabla, line_chart, winners_chart
    tabla = getIndicadorAnio(rating_promedio_df, '2020', '2025')
    line_chart = dcc.Graph(figure=create_line_chart(time_series_df, 2020, 2025))
    winners_chart = dcc.Graph(figure=get_monthly_winners(time_series_df, 2020, 2025))
    return tabla, line_chart, winners_chart

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
     Input('dropdown-num-lenguajes', 'value'),
     Input('selected-language-store', 'data')]
)
def actualizar_heatmap(anio_seleccionado, num_lenguajes, selected_language):
    """
    Callback que actualiza el heatmap cuando se selecciona un año diferente
    o cuando cambia el lenguaje seleccionado
    """
    return crear_heatmap_quarters(anio_seleccionado, num_lenguajes, selected_language)

# Callback para actualizar los medidores
@app.callback(
    Output('medidores-promedio', 'figure'),
    [Input('dropdown-anio', 'value'),
     Input('dropdown-num-lenguajes', 'value'),
     Input('selected-language-store', 'data')]
)
def actualizar_medidores(anio_seleccionado, num_lenguajes, selected_language):
    """
    Callback que actualiza los medidores cuando se selecciona un año diferente,
    se cambia el número de lenguajes o cuando cambia el lenguaje seleccionado
    """
    return crear_medidores_promedio(anio_seleccionado, num_lenguajes, selected_language)


# ============================================================================
# CALLBACKS PARA INTERACTIVIDAD TIPO POWER BI
# ============================================================================

# Callback para actualizar el store cuando se hace clic en la tabla
@app.callback(
    Output('selected-language-store', 'data'),
    [Input('tabla-indicador', 'active_cell'),
     Input('grafico-promedio-estrellas', 'clickData')],
    [State('tabla-indicador', 'data'),
     State('selected-language-store', 'data')],
    prevent_initial_call=True
)
def update_selected_language(active_cell, click_data_stars, table_data, current_selection):
    """
    Actualiza el lenguaje seleccionado basado en clics en tabla o gráficos
    """
    from dash import ctx

    triggered_id = ctx.triggered_id

    if triggered_id == 'tabla-indicador' and active_cell:
        row_idx = active_cell['row']
        selected_lang = table_data[row_idx]['Language']
        # Si se hace clic en el mismo lenguaje, deseleccionar
        if selected_lang == current_selection:
            return None
        return selected_lang

    elif triggered_id == 'grafico-promedio-estrellas' and click_data_stars:
        selected_lang = click_data_stars['points'][0]['x']
        if selected_lang == current_selection:
            return None
        return selected_lang

    return current_selection


# Callback para actualizar Sección 1 con selección de lenguaje
@app.callback(
    Output('tabla-container', 'children', allow_duplicate=True),
    Output('timeseries-container', 'children', allow_duplicate=True),
    Output('winners-container', 'children', allow_duplicate=True),
    [Input('selected-language-store', 'data')],
    [State('year-range-slider', 'value')],
    prevent_initial_call=True
)
def update_section1_with_selection(selected_language, year_range):
    """
    Actualiza la sección 1 cuando cambia el lenguaje seleccionado
    """
    if year_range and len(year_range) == 2:
        year1, year2 = str(year_range[0]), str(year_range[1])
        tabla = getIndicadorAnio(rating_promedio_df, year1, year2, selected_language)
        line_chart = dcc.Graph(
            figure=create_line_chart(time_series_df, year_range[0], year_range[1], selected_language),
            id='grafico-line-chart'
        )
        winners_chart = dcc.Graph(
            figure=get_monthly_winners(time_series_df, year_range[0], year_range[1], selected_language),
            id='grafico-winners'
        )
        return tabla, line_chart, winners_chart

    tabla = getIndicadorAnio(rating_promedio_df, '2020', '2025', selected_language)
    line_chart = dcc.Graph(
        figure=create_line_chart(time_series_df, 2020, 2025, selected_language),
        id='grafico-line-chart'
    )
    winners_chart = dcc.Graph(
        figure=get_monthly_winners(time_series_df, 2020, 2025, selected_language),
        id='grafico-winners'
    )
    return tabla, line_chart, winners_chart


# Callback para actualizar gráfico de estrellas con selección
@app.callback(
    Output('grafico-promedio-estrellas', 'figure'),
    [Input('selected-language-store', 'data')]
)
def update_stars_chart(selected_language):
    """
    Actualiza el gráfico de promedio de estrellas con el lenguaje seleccionado
    """
    return crear_grafico_promedio_estrellas(selected_language)


# Callback para sincronizar el dropdown de lenguaje con la selección
@app.callback(
    Output('dropdown-lenguaje', 'value'),
    [Input('selected-language-store', 'data')],
    [State('dropdown-lenguaje', 'options')],
    prevent_initial_call=True
)
def sync_dropdown_with_selection(selected_language, dropdown_options):
    """
    Sincroniza el dropdown de lenguaje con la selección global
    """
    if selected_language:
        # Verificar si el lenguaje existe en las opciones del dropdown
        available_languages = [opt['value'] for opt in dropdown_options]
        if selected_language in available_languages:
            return selected_language
    return dash.no_update


# ============================================================================
# CALLBACKS PARA EL CHATBOT IA
# ============================================================================

# Inicializar agente IA (solo si esta disponible)
ai_agent = None
if AI_AVAILABLE:
    try:
        ai_agent = CodeTrendsAgent()
        print("CodeTrends AI Agent inicializado correctamente!")
    except Exception as e:
        print(f"Error inicializando agente IA: {e}")
        AI_AVAILABLE = False


@app.callback(
    [Output('chat-history', 'children'),
     Output('chat-input', 'value'),
     Output('chat-history-store', 'data'),
     Output('chat-loading-output', 'children')],
    [Input('send-button', 'n_clicks'),
     Input('chat-input', 'n_submit'),
     Input('clear-button', 'n_clicks'),
     Input('quick-q1', 'n_clicks'),
     Input('quick-q2', 'n_clicks'),
     Input('quick-q3', 'n_clicks'),
     Input('quick-q4', 'n_clicks')],
    [State('chat-input', 'value'),
     State('chat-history', 'children'),
     State('chat-history-store', 'data')],
    prevent_initial_call=True
)
def handle_chat(send_clicks, enter_submit, clear_clicks,
                q1_clicks, q2_clicks, q3_clicks, q4_clicks,
                user_input, chat_children, history_data):
    """
    Maneja todas las interacciones del chat
    """
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, ""

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Colores para los mensajes
    user_style = {
        'marginBottom': '10px',
        'padding': '10px',
        'backgroundColor': '#e3f2fd',
        'borderRadius': '8px',
        'marginLeft': '20%'
    }
    ai_style = {
        'marginBottom': '10px',
        'padding': '10px',
        'backgroundColor': 'white',
        'borderRadius': '8px',
        'marginRight': '20%',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
    }

    # Manejar boton de limpiar
    if triggered_id == 'clear-button':
        if ai_agent:
            ai_agent.clear_history()
        initial_message = html.Div([
            html.Strong("CodeTrends AI: ", style={'color': '#4292c6'}),
            html.Span(
                "Historial limpiado. Como puedo ayudarte?",
                style={'color': '#08306b'}
            )
        ], style=ai_style)
        return [initial_message], '', [], ""

    # Determinar el mensaje a enviar
    message = None

    if triggered_id in ['send-button', 'chat-input'] and user_input:
        message = user_input
    elif triggered_id == 'quick-q1':
        message = "Cual es el mejor lenguaje para aprender en 2025?"
    elif triggered_id == 'quick-q2':
        message = "Compara Python vs JavaScript para desarrollo web"
    elif triggered_id == 'quick-q3':
        message = "Que lenguajes deberia aprender para trabajar en Inteligencia Artificial?"
    elif triggered_id == 'quick-q4':
        message = "Deberia aprender Rust o Go? Cual tiene mejor futuro?"

    if not message:
        return dash.no_update, dash.no_update, dash.no_update, ""

    # Crear mensaje del usuario
    user_message = html.Div([
        html.Strong("Tu: ", style={'color': '#1976d2'}),
        html.Span(message, style={'color': '#08306b'})
    ], style=user_style)

    # Obtener respuesta de la IA
    if ai_agent and AI_AVAILABLE:
        try:
            ai_response = ai_agent.query(message)
        except Exception as e:
            ai_response = f"Lo siento, ocurrio un error: {str(e)}"
    else:
        ai_response = (
            "El asistente IA no esta disponible. "
            "Por favor configura tu API key de Claude en el archivo .env\n\n"
            "Pasos:\n"
            "1. Abre el archivo .env en la carpeta del proyecto\n"
            "2. Reemplaza 'tu-api-key-aqui' con tu API key\n"
            "3. Obtener key en: https://console.anthropic.com/"
        )

    # Crear mensaje de la IA
    ai_message = html.Div([
        html.Strong("CodeTrends AI: ", style={'color': '#4292c6'}),
        dcc.Markdown(
            ai_response,
            style={'color': '#08306b', 'marginTop': '5px'}
        )
    ], style=ai_style)

    # Actualizar historial
    new_children = (chat_children or []) + [user_message, ai_message]

    # Limitar historial visual a ultimos 20 mensajes
    if len(new_children) > 40:
        new_children = new_children[-40:]

    return new_children, '', history_data, ""


if __name__ == '__main__':
    app.run(debug=True, port=8050)
