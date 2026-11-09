
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from audit_engine import run_audit

from analysis_tools import (
    analyze_campaigns,
    analyze_funnel,
    compare_periods
)


# ==========================================
# 1. HERRAMIENTAS DISPONIBLES
# ==========================================

def get_available_tools():

    return {
        "run_audit": run_audit,
        "analyze_campaigns": analyze_campaigns,
        "analyze_funnel": analyze_funnel,
        "compare_periods": compare_periods
    }


# ==========================================
# 2. EJECUTAR AUDITORÍA
# ==========================================

def execute_audit():

    results = run_audit("google_ads_audit.csv")

    return {
        "message": "Auditoría ejecutada correctamente.",
        "campaigns_analyzed": len(results),
        "results": results
    }


# ==========================================
# 3. COMPARAR SEPTIEMBRE VS OCTUBRE
# ==========================================

def execute_period_comparison():

    september_results = run_audit(
        "google_ads_audit.csv"
    )

    october_results = run_audit(
        "google_ads_audit_october.csv"
    )

    comparison = compare_periods(
        september_results,
        october_results
    )

    return {
        "message": "Comparación de septiembre y octubre ejecutada correctamente.",
        "periods": [
            "Septiembre",
            "Octubre"
        ],
        "campaigns_compared": len(comparison),
        "results": comparison
    }


# ==========================================
# 4. CONEXIÓN CON OPENAI
# ==========================================

def test_openai_connection():

    load_dotenv(dotenv_path=".env")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "No se encontró OPENAI_API_KEY en el archivo .env"
        )

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input="Responde únicamente: Hola, agente de Google Ads conectado."
    )

    print(response.output_text)


# ==========================================
# 5. DEFINICIÓN DE HERRAMIENTAS PARA LA IA
# ==========================================

def get_tool_definitions():

    return [
        {
            "type": "function",
            "name": "run_audit",
            "description": (
                "Ejecuta la auditoría de Google Ads sobre el CSV "
                "de septiembre. Calcula las métricas y devuelve "
                "los resultados de todas las campañas."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        },
        {
            "type": "function",
            "name": "analyze_campaigns",
            "description": (
                "Analiza los resultados de la auditoría. "
                "Identifica las tres campañas con mejor y peor CPA "
                "y calcula el CPA promedio. "
                "Requiere que run_audit se haya ejecutado antes."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        },
        {
            "type": "function",
            "name": "analyze_funnel",
            "description": (
                "Analiza el funnel por campaña y globalmente. "
                "Calcula conversiones, tasas y pérdidas entre etapas. "
                "Identifica las campañas con mayores pérdidas absolutas "
                "y peores tasas de conversión. "
                "Devuelve tasas globales ponderadas. "
                "Requiere que run_audit se haya ejecutado antes."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        },
        {
            "type": "function",
            "name": "compare_periods",
            "description": (
                "Compara el rendimiento de las campañas entre "
                "septiembre y octubre. Utiliza los archivos "
                "google_ads_audit.csv y google_ads_audit_october.csv. "
                "Devuelve CPA de ambos periodos, variación porcentual "
                "del CPA, variación de inversión y variación de aperturas. "
                "Es indispensable cuando el usuario pregunta qué campañas "
                "mejoraron o empeoraron entre ambos periodos."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }
    ]


# ==========================================
# 6. EJECUTAR HERRAMIENTAS
# ==========================================

def execute_tool_call(tool_name, arguments, context):

    if tool_name == "run_audit":

        if "audit_results" in context:

            return {
                "message": "La auditoría ya fue ejecutada.",
                "campaigns_analyzed": len(context["audit_results"]),
                "results": context["audit_results"]
            }

        result = execute_audit()

        context["audit_results"] = result["results"]

        return result

    elif tool_name == "analyze_campaigns":

        if "audit_results" not in context:
            raise ValueError(
                "Primero debes ejecutar la auditoría."
            )

        return analyze_campaigns(
            context["audit_results"]
        )

    elif tool_name == "analyze_funnel":

        if "audit_results" not in context:
            raise ValueError(
                "Primero debes ejecutar la auditoría."
            )

        return analyze_funnel(
            context["audit_results"]
        )

    elif tool_name == "compare_periods":

        if "period_comparison" in context:

            return context["period_comparison"]

        result = execute_period_comparison()

        context["period_comparison"] = result

        return result

    else:

        raise ValueError(
            f"Herramienta no permitida: {tool_name}"
        )


# ==========================================
# 7. INSTRUCCIONES DEL AGENTE
# ==========================================

def get_agent_instructions():

    return (
        "Eres un agente especializado en Google Ads, "
        "performance marketing y adquisición digital. "

        "Tu objetivo es investigar datos, identificar problemas "
        "y elaborar diagnósticos basados en evidencias. "

        "Tienes cuatro herramientas disponibles: "
        "run_audit, analyze_campaigns, analyze_funnel "
        "y compare_periods. "

        "REGLAS DE EJECUCIÓN: "

        "1. Ejecuta run_audit cuando la pregunta requiera "
        "analizar campañas del periodo de septiembre. "

        "2. Utiliza analyze_campaigns para comparar CPA "
        "e identificar las mejores y peores campañas. "

        "3. Si el usuario solicita comparar tasas de conversión "
        "individuales contra promedios globales, ejecuta "
        "analyze_funnel antes de responder. "

        "4. Nunca sustituyas los promedios calculados por "
        "las herramientas por estimaciones o benchmarks "
        "no disponibles. "

        "5. Si el usuario pregunta qué campañas mejoraron "
        "o empeoraron entre septiembre y octubre, ejecuta "
        "compare_periods. "

        "6. Utiliza compare_periods para investigar cambios "
        "en CPA, inversión y aperturas entre ambos periodos. "

        "7. No ejecutes herramientas innecesarias. "
        "Selecciona las herramientas según la pregunta. "

        "8. No repitas herramientas si ya tienes sus resultados. "

        "REGLAS DE ANÁLISIS: "

        "1. Distingue siempre pérdidas absolutas de eficiencia "
        "de conversión. "

        "2. Compara las tasas individuales contra los promedios "
        "globales calculados por las herramientas. "

        "3. No clasifiques una campaña como problemática "
        "únicamente por su volumen de pérdidas. "

        "4. Considera el volumen de datos antes de interpretar "
        "una tasa de conversión. "

        "5. No confundas correlación con causalidad. "

        "6. Para comparaciones entre periodos, interpreta "
        "conjuntamente los cambios de CPA, inversión y aperturas. "

        "7. Un aumento del CPA representa un deterioro de "
        "eficiencia, pero investiga si se explica por mayor "
        "inversión, menor número de aperturas o ambos. "

        "8. Una reducción del CPA representa una mejora "
        "de eficiencia, pero no necesariamente un crecimiento "
        "del volumen de aperturas. "

        "9. Si los indicadores permanecen iguales, reporta "
        "que no hubo cambios observados. "

        "10. No inventes causas para explicar las variaciones. "

        "REGLAS DE PRIORIZACIÓN: "

        "Prioriza los problemas considerando impacto absoluto, "
        "eficiencia de conversión y desviación del CPA respecto "
        "a su objetivo. "

        "Para comparar periodos, considera la magnitud del "
        "deterioro del CPA y los cambios en aperturas e inversión. "

        "No inventes índices numéricos de prioridad ni impactos "
        "económicos que los datos no permiten determinar. "

        "REGLAS DE RECOMENDACIÓN: "

        "1. No recomiendes aumentar, escalar ni redistribuir "
        "presupuesto con los datos actualmente disponibles. "

        "2. Un CPA favorable no demuestra por sí solo que una "
        "campaña pueda absorber más presupuesto. "

        "3. Para evaluar oportunidades de escalamiento se "
        "necesitan datos de presupuesto, impresiones, cuota "
        "de impresiones, saturación, tendencias históricas, "
        "CPA marginal o experimentos incrementales. "

        "4. Propón acciones de investigación y optimización "
        "respaldadas por los datos disponibles. "

        "5. Relaciona cada recomendación con un hallazgo concreto. "

        "REGLAS DE RESPUESTA: "

        "Presenta un diagnóstico claro y organizado. "

        "Para comparaciones entre periodos incluye: "
        "campañas que empeoraron, campañas que mejoraron, "
        "campañas sin cambios, variaciones de CPA, inversión "
        "y aperturas. "

        "Diferencia hechos comprobados de hipótesis. "

        "No inventes métricas, fechas ni afirmes que investigaste "
        "información que no está disponible. "

        "Si faltan datos para responder, explica cuáles "
        "necesitas y para qué."
    )


# ==========================================
# 8. AGENTE DE GOOGLE ADS CON CONVERSACIÓN
# ==========================================

def run_agent(
    question,
    context=None,
    previous_response_id=None,
    return_state=False
):

    load_dotenv(dotenv_path=".env")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "No se encontró OPENAI_API_KEY en el archivo .env"
        )

    client = OpenAI(api_key=api_key)

    instructions = get_agent_instructions()
    tools = get_tool_definitions()

    # Conserva el contexto de las herramientas
    if context is None:
        context = {}

    # Primera pregunta de la conversación
    if previous_response_id is None:

        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=instructions,
            input=question,
            tools=tools
        )

    # Pregunta de seguimiento
    else:

        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=instructions,
            previous_response_id=previous_response_id,
            input=question,
            tools=tools
        )

    # Ciclo de ejecución de herramientas
    for iteration in range(5):

        function_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        # Si no solicita más herramientas, termina
        if not function_calls:
            break

        tool_outputs = []

        for call in function_calls:

            print("Ejecutando herramienta:", call.name)

            arguments = json.loads(call.arguments)

            result = execute_tool_call(
                call.name,
                arguments,
                context
            )

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(
                    result,
                    ensure_ascii=False
                )
            })

        # Enviar los resultados de las herramientas al modelo
        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=instructions,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=tools
        )

    else:

        raise RuntimeError(
            "El agente alcanzó el límite de 5 ciclos de herramientas."
        )

    # Devolver la respuesta y el estado de la conversación
    result = {
        "answer": response.output_text,
        "response_id": response.id,
        "context": context
    }

    # Permitir que Streamlit reciba el estado completo
    if return_state:
        return result

    # Mantener compatibilidad con las pruebas anteriores
    return response.output_text

