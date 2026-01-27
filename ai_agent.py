# ===========================================
# CodeTrends AI Agent - Asistente Conversacional
# ===========================================

import anthropic
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class CodeTrendsAgent:
    """
    Agente de IA conversacional para analizar tendencias de lenguajes de programación.
    Utiliza Claude API de Anthropic.
    """

    def __init__(self, api_key=None):
        """
        Inicializar el agente con la API key de Claude.

        Args:
            api_key: API key de Anthropic. Si no se proporciona, se busca en .env
        """
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')

        if not self.api_key or self.api_key == 'tu-api-key-aqui':
            raise ValueError(
                "API Key no configurada. Por favor:\n"
                "1. Abre el archivo .env\n"
                "2. Reemplaza 'tu-api-key-aqui' con tu API key de Claude\n"
                "3. Obtener en: https://console.anthropic.com/"
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.knowledge_base = self._load_knowledge_base()
        self.conversation_history = []

    def _load_knowledge_base(self):
        """Cargar todos los datasets y crear contexto para la IA"""
        knowledge = {
            'metadata': {
                'period': '2020-2025',
                'sources': ['GitHub Trending', 'TIOBE Index', 'Madnight Pull Requests'],
                'languages': [
                    'Python', 'Java', 'JavaScript', 'C++', 'C', 'C#', 'Go', 'Rust',
                    'PHP', 'Kotlin', 'R', 'MATLAB', 'Perl', 'Assembly', 'Fortran'
                ]
            },
            'insights': self._generate_insights()
        }

        # Cargar datasets si existen
        try:
            # Series de tiempo TIOBE
            tiobe_df = pd.read_csv('Datos/Series_de_Tiempo.csv')
            knowledge['tiobe_summary'] = self._summarize_tiobe(tiobe_df)
        except:
            knowledge['tiobe_summary'] = "Datos TIOBE no disponibles"

        try:
            # GitHub Trending
            github_df = pd.read_csv('Datos_procesados/Estadisticas_lenguajes.csv')
            knowledge['github_summary'] = self._summarize_github(github_df)
        except:
            knowledge['github_summary'] = "Datos GitHub no disponibles"

        try:
            # Pull Requests
            pr_df = pd.read_csv('Datos/Pull_Requests.csv')
            knowledge['pr_summary'] = self._summarize_pr(pr_df)
        except:
            knowledge['pr_summary'] = "Datos Pull Requests no disponibles"

        return knowledge

    def _generate_insights(self):
        """Generar insights clave del análisis"""
        return """
        INSIGHTS PRINCIPALES DEL ANALISIS 2020-2025:

        1. PYTHON - LIDER ABSOLUTO:
           - 50 meses como #1 en TIOBE (70.4% del periodo)
           - Crecimiento: +14.59 puntos (10.07% -> 24.66%)
           - Promedio estrellas GitHub: 26,328
           - Pull Requests promedio: 17.55%
           - Dominios: IA, ML, Data Science, Automatizacion

        2. LENGUAJES EN ASCENSO:
           - Go: Crecimiento constante, popular en cloud/DevOps
           - Rust: Mayor crecimiento relativo, enfoque en seguridad
           - Kotlin: Adopcion en Android, respaldado por Google

        3. LENGUAJES ESTABLES:
           - Java: Mantiene relevancia empresarial (11.35% PR promedio)
           - JavaScript: Dominio en web frontend/backend
           - C++: Estable en sistemas y gaming

        4. LENGUAJES EN DECLIVE:
           - PHP: Perdida gradual de popularidad
           - Perl: Uso muy reducido
           - Assembly: Nicho muy especializado

        5. TENDENCIAS CLAVE:
           - IA/ML impulsa Python dramaticamente desde 2023
           - Cloud computing favorece Go y Rust
           - Desarrollo movil consolida Kotlin y Swift
           - WebAssembly abre nuevas posibilidades para Rust/C++
        """

    def _summarize_tiobe(self, df):
        """Resumir datos de TIOBE"""
        try:
            latest = df.groupby('Language')['Rating'].last()
            top_5 = latest.nlargest(5)
            return f"Top 5 TIOBE actual: {', '.join([f'{lang}: {val:.2f}%' for lang, val in top_5.items()])}"
        except:
            return "Resumen TIOBE no disponible"

    def _summarize_github(self, df):
        """Resumir datos de GitHub"""
        try:
            top_stars = df.nlargest(5, 'Promedio_Stars')[['Language', 'Promedio_Stars']]
            return f"Top 5 GitHub por estrellas promedio: {top_stars.to_dict('records')}"
        except:
            return "Resumen GitHub no disponible"

    def _summarize_pr(self, df):
        """Resumir datos de Pull Requests"""
        try:
            avg_pr = df.groupby('Lenguaje')['Porcentaje'].mean().nlargest(5)
            return f"Top 5 por Pull Requests: {', '.join([f'{lang}: {val:.2f}%' for lang, val in avg_pr.items()])}"
        except:
            return "Resumen PR no disponible"

    def _build_system_prompt(self):
        """Construir el prompt del sistema con todo el contexto"""
        return f"""Eres "CodeTrends AI", un asistente experto en analisis de lenguajes de programacion.

CONTEXTO Y DATOS DISPONIBLES:
{json.dumps(self.knowledge_base, indent=2, ensure_ascii=False)}

TU ROL:
1. Responder preguntas sobre tendencias de lenguajes de programacion (2020-2025)
2. Comparar lenguajes basandote en datos reales
3. Recomendar lenguajes segun el perfil del usuario
4. Explicar tendencias y predecir direcciones futuras
5. Dar consejos de carrera basados en datos

REGLAS:
- Siempre basa tus respuestas en los datos proporcionados
- Se conciso pero informativo (maximo 300 palabras)
- Usa emojis para hacer las respuestas mas amigables
- Si no tienes datos especificos, indicalo claramente
- Menciona las fuentes (TIOBE, GitHub, Pull Requests) cuando sea relevante
- Responde en espanol

EJEMPLOS DE PREGUNTAS QUE PUEDES RESPONDER:
- "Cual es el mejor lenguaje para aprender en 2025?"
- "Compara Python vs JavaScript para desarrollo web"
- "Que lenguaje tiene mejor futuro para IA?"
- "Deberia aprender Rust o Go?"
- "Como ha evolucionado Java en los ultimos 5 anos?"
"""

    def query(self, user_message):
        """
        Procesar una pregunta del usuario y obtener respuesta de Claude.

        Args:
            user_message: Pregunta del usuario

        Returns:
            Respuesta del asistente IA
        """
        try:
            # Agregar mensaje del usuario al historial
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Limitar historial a ultimas 10 interacciones
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            # Llamar a Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=self._build_system_prompt(),
                messages=self.conversation_history
            )

            # Extraer respuesta
            assistant_message = response.content[0].text

            # Agregar respuesta al historial
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except anthropic.APIConnectionError:
            return "Error de conexion. Verifica tu conexion a internet."
        except anthropic.RateLimitError:
            return "Limite de API alcanzado. Intenta de nuevo en unos segundos."
        except anthropic.APIStatusError as e:
            return f"Error de API: {e.message}"
        except Exception as e:
            return f"Error inesperado: {str(e)}"

    def clear_history(self):
        """Limpiar el historial de conversacion"""
        self.conversation_history = []
        return "Historial de conversacion limpiado."

    def get_quick_insight(self, language):
        """
        Obtener un insight rapido sobre un lenguaje especifico.

        Args:
            language: Nombre del lenguaje

        Returns:
            Insight rapido sobre el lenguaje
        """
        prompt = f"Dame un resumen rapido (3-4 oraciones) sobre {language} basandote en los datos 2020-2025. Incluye: tendencia, fortalezas y para quien es recomendado."
        return self.query(prompt)

    def compare_languages(self, lang1, lang2):
        """
        Comparar dos lenguajes.

        Args:
            lang1: Primer lenguaje
            lang2: Segundo lenguaje

        Returns:
            Comparacion detallada
        """
        prompt = f"Compara {lang1} vs {lang2} en una tabla con: Popularidad, Crecimiento, Casos de uso, Dificultad de aprendizaje, y Perspectiva futura. Basate en los datos 2020-2025."
        return self.query(prompt)

    def recommend_for_career(self, career_goal):
        """
        Recomendar lenguajes segun objetivo de carrera.

        Args:
            career_goal: Objetivo de carrera del usuario

        Returns:
            Recomendaciones personalizadas
        """
        prompt = f"Quiero ser {career_goal}. Basandote en los datos 2020-2025, recomiendame los 3 mejores lenguajes para aprender, en orden de prioridad, con una breve justificacion para cada uno."
        return self.query(prompt)


# Funcion para crear agente facilmente
def create_agent(api_key=None):
    """
    Crear una instancia del agente CodeTrends.

    Args:
        api_key: API key de Claude (opcional si esta en .env)

    Returns:
        Instancia de CodeTrendsAgent
    """
    return CodeTrendsAgent(api_key)


# Test del agente
if __name__ == "__main__":
    print("Probando CodeTrends AI Agent...")

    try:
        agent = create_agent()
        print("Agente creado exitosamente!")

        # Test basico
        response = agent.query("Hola! Cual es el lenguaje mas popular actualmente?")
        print(f"\nRespuesta: {response}")

    except ValueError as e:
        print(f"\nError de configuracion: {e}")
    except Exception as e:
        print(f"\nError: {e}")
