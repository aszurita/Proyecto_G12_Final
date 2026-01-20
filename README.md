# Análisis de Tendencias y Popularidad de Lenguajes de Programación

**Proyecto de Lenguajes de Programación - Grupo 12**

**Integrantes:**
- José Marin Molina
- Dhamar Quishpe Rivera
- Angelo Zurita Guerrero

## Descripción del Proyecto

Este proyecto analiza la popularidad, actividad de desarrollo y tendencias históricas de lenguajes de programación mediante la integración de datos de tres fuentes principales:

1. **GitHub Trending**: Análisis de repositorios populares y métricas de estrellas
2. **TIOBE Index**: Rankings históricos y tendencias de popularidad (2020-2024)
3. **Madnight GitHub**: Datos de Pull Requests y contribuciones de la comunidad

El dashboard interactivo permite explorar y visualizar estos datos de manera integrada y profesional.

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Proyecto_G12_Final
```

### 2. Crear un entorno virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Las dependencias principales son:

FRONTED
Lenguaje Usado : Python
- dash
- dash-bootstrap-components
- plotly
  
BACKEND (Scrapping)
Lenguaje Usado : Ruby
- Nokogiri
- Selenium
## Estructura del Proyecto

PREPROCESAMIENTO
Lenguaje Usado : Python
- pandas
- re
```
Proyecto_G12_Final/
├── Datos/                          # Carpeta con datos extraídos
│   ├── TopRepositorios.csv         # Repositorios trending generales
│   ├── TopReposXLenguajes.csv      # Top repositorios por lenguaje
│   ├── RankingTIOBE2025.csv        # Ranking TIOBE actual
│   ├── Series_de_Tiempo.csv        # Series históricas TIOBE
│   └── MadnightPullRequests.csv    # Datos de Pull Requests
├── Scrapping/                      # Scripts de web scraping en Ruby
│   ├── GitHubScraper.rb
│   ├── TiobeScraper.rb
│   └── madnight_scraping.rb
├── main.py                         # Dashboard principal
├── requirements.txt                # Dependencias de Python
├── Plantilla_Propuesta_LP_2025_P1_12.pdf  # Documento del proyecto
└── README.md                       # Este archivo
```

## Ejecución del Dashboard

### 1. Activar el entorno virtual (si no está activado)

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Ejecutar el dashboard

```bash
python main.py
```

### 3. Acceder al dashboard

Abrir el navegador y acceder a:
```
http://127.0.0.1:8050/
```

o

```
http://localhost:8050/
```

### 4. Detener el servidor

Presionar `Ctrl + C` en la terminal donde se está ejecutando el dashboard.

## Funcionalidades del Dashboard

### Panel de Control
- **Selector de Lenguaje**: Permite filtrar visualizaciones por lenguaje de programación
- **Rango de Años**: Ajusta el período temporal del análisis (2020-2025)

### Sección 1: Actividad en Repositorios (GitHub Trending)
1. **Promedio de Estrellas por Lenguaje**: Gráfico de barras comparativo
2. **Top Repositorios Más Populares**: Los 10 repositorios con más estrellas
3. **Top 5 por Lenguaje**: Comparación de estrellas vs forks por lenguaje seleccionado

### Sección 2: Popularidad y Tendencias (TIOBE Index)
1. **Series de Tiempo Históricas**: Evolución de popularidad 2020-2024
2. **Indicadores de Crecimiento**: Tabla con cambios porcentuales 2024-2025
3. **Apariciones en Top 1**: Lenguajes que más veces han liderado el ranking

### Sección 3: Contribuciones de Desarrollo (Pull Requests)
1. **Heatmap de Estacionalidad**: Visualización de PRs por trimestre y año
2. **Medidor de Promedio**: Indicador gauge del promedio de PRs por lenguaje
3. **Lenguajes en Top 1**: Ranking de lenguajes con más PRs liderando

## Notas Técnicas

### Web Scraping
Los datos fueron extraídos mediante scripts en Ruby ubicados en la carpeta `Scrapping/`:
- **GitHubScraper.rb**: Extrae datos de GitHub Trending
- **TiobeScraper.rb**: Obtiene rankings históricos de TIOBE
- **madnight_scraping.rb**: Extrae datos de Pull Requests

### Formato de Datos
- Los datos de estrellas y forks de GitHub están en formato numérico (comas removidas automáticamente)
- Las fechas en Series_de_Tiempo están en formato YYYY-MM-DD
- Los porcentajes de Pull Requests son procesados automáticamente por el dashboard

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'dash'"
```bash
pip install -r requirements.txt
```

### El dashboard no carga datos
Verificar que la carpeta `Datos/` contenga todos los archivos CSV necesarios.



