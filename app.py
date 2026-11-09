
import streamlit as st
import pandas as pd

from agent import run_agent


# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Google Ads Growth Agent",
    page_icon="📊",
    layout="wide"
)

st.title("Google Ads Performance Audit")
st.caption("Dashboard de performance y análisis con inteligencia artificial")


# ==========================================
# 2. MEMORIA DE CONVERSACIÓN
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_context" not in st.session_state:
    st.session_state.agent_context = {}

if "previous_response_id" not in st.session_state:
    st.session_state.previous_response_id = None


# ==========================================
# 3. FUNCIÓN PARA REINICIAR CONVERSACIÓN
# ==========================================

def reset_conversation():

    st.session_state.messages = []
    st.session_state.agent_context = {}
    st.session_state.previous_response_id = None


# ==========================================
# 4. VENTANA EMERGENTE DEL AGENTE
# ==========================================

@st.dialog(
    "Conversación con tu agente de Growth",
    width="large"
)
def chat_dialog():

    st.caption(
        "Pregunta sobre tus campañas utilizando lenguaje natural."
    )

    # Espacio donde aparecerá el historial
    history_placeholder = st.empty()

    # Formulario para enviar preguntas
    with st.form(
        "agent_chat_form",
        clear_on_submit=True
    ):

        question = st.text_area(
            "Escribe tu consulta",
            placeholder=(
                "Ejemplo: ¿Qué campañas empeoraron "
                "de septiembre a octubre?"
            ),
            height=100
        )

        submitted = st.form_submit_button(
            "Enviar pregunta",
            type="primary",
            use_container_width=True
        )

    # Procesar pregunta
    if submitted and question.strip():

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        try:

            with st.spinner(
                "Analizando tus datos y consultando herramientas..."
            ):

                result = run_agent(
                    question=question,
                    context=st.session_state.agent_context,
                    previous_response_id=(
                        st.session_state.previous_response_id
                    ),
                    return_state=True
                )

                answer = result["answer"]

                st.session_state.agent_context = result["context"]

                st.session_state.previous_response_id = (
                    result["response_id"]
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

        except Exception as error:

            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    f"No fue posible obtener una respuesta: {error}"
                )
            })

    # Mostrar historial actualizado
    with history_placeholder.container():

        if not st.session_state.messages:

            st.info(
                "¡Hola! Soy tu agente de Growth. "
                "¿Qué te gustaría investigar?"
            )

        for message in st.session_state.messages:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Reiniciar conversación desde el popup
    if st.button(
        "Nueva conversación",
        use_container_width=True
    ):

        reset_conversation()
        st.rerun()


# ==========================================
# 5. BARRA LATERAL
# ==========================================

with st.sidebar:

    st.title("Google Ads Agent")

    st.write(
        "Consulta el rendimiento de tus campañas "
        "y conversa con tu agente de IA."
    )

    st.divider()

    if st.button(
        "Nueva conversación",
        use_container_width=True
    ):

        reset_conversation()
        st.rerun()


# ==========================================
# 6. BOTÓN PARA ABRIR EL POPUP
# ==========================================

if st.button(
    "💬 Consultar agente IA",
    type="primary",
    use_container_width=False
):

    chat_dialog()


# ==========================================
# 7. DASHBOARD DE GOOGLE ADS
# ==========================================

st.header("Dashboard de rendimiento")

try:

    df = pd.read_csv("audit_results.csv")

    total_spend = df["spend"].sum()
    total_opened_accounts = df["opened_accounts"].sum()

    overall_cpa = (
        total_spend / total_opened_accounts
        if total_opened_accounts > 0
        else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Inversión total",
        f"${total_spend:,.0f}"
    )

    col2.metric(
        "Cuentas aperturadas",
        f"{total_opened_accounts:,.0f}"
    )

    col3.metric(
        "CPA general",
        f"${overall_cpa:,.2f}"
    )

    # RESUMEN EJECUTIVO

    st.subheader("Resumen ejecutivo")

    requires_attention = df[
        df["calculated_performance_status"] == "Requiere atención"
    ]["campaign"].tolist()

    monitor = df[
        df["calculated_performance_status"] == "Monitorear"
    ]["campaign"].tolist()

    meets_target = df[
        df["calculated_performance_status"] == "Cumple"
    ]["campaign"].tolist()

    if requires_attention:
        st.error(
            "Requieren atención: " + ", ".join(requires_attention)
        )

    if monitor:
        st.warning(
            "Monitorear: " + ", ".join(monitor)
        )

    if meets_target:
        st.success(
            "Cumplen el objetivo: " + ", ".join(meets_target)
        )

    # CPA REAL VS CPA OBJETIVO

    st.subheader("CPA real vs CPA objetivo")

    chart_data = df.set_index("campaign")[[
        "calculated_cpa",
        "target_cpa"
    ]].rename(columns={
        "calculated_cpa": "CPA real",
        "target_cpa": "CPA objetivo"
    })

    st.bar_chart(
        chart_data,
        stack=False
    )

    # RESULTADOS POR CAMPAÑA

    st.subheader("Resultados por campaña")

    summary_table = df[[
        "campaign",
        "campaign_type",
        "spend",
        "opened_accounts",
        "calculated_cpa",
        "target_cpa",
        "calculated_cpa_vs_target",
        "calculated_performance_status"
    ]].copy()

    summary_table["calculated_cpa_vs_target"] = (
        summary_table["calculated_cpa_vs_target"] * 100
    )

    summary_table = summary_table.rename(columns={
        "campaign": "Campaña",
        "campaign_type": "Tipo",
        "spend": "Inversión",
        "opened_accounts": "Cuentas aperturadas",
        "calculated_cpa": "CPA real",
        "target_cpa": "CPA objetivo",
        "calculated_cpa_vs_target": "CPA vs objetivo",
        "calculated_performance_status": "Estatus"
    })

    def colorear_estatus(valor):

        colores = {
            "Cumple": "background-color: #C6EFCE; color: #006100;",
            "Monitorear": "background-color: #FFEB9C; color: #9C6500;",
            "Requiere atención": "background-color: #FFC7CE; color: #9C0006;"
        }

        return colores.get(valor, "")

    tabla_estilizada = summary_table.style.map(
        colorear_estatus,
        subset=["Estatus"]
    )

    st.dataframe(
        tabla_estilizada,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Inversión": st.column_config.NumberColumn(format="$%.0f"),
            "CPA real": st.column_config.NumberColumn(format="$%.2f"),
            "CPA objetivo": st.column_config.NumberColumn(format="$%.2f"),
            "CPA vs objetivo": st.column_config.NumberColumn(format="%.1f%%")
        }
    )

    # RECOMENDACIONES POR CAMPAÑA

    st.subheader("Recomendaciones por campaña")

    for _, row in df.iterrows():

        with st.expander(
            f'{row["campaign"]} — {row["calculated_performance_status"]}'
        ):

            st.write(
                row["calculated_recommendation"]
            )

except FileNotFoundError:

    st.warning(
        "No se encontró audit_results.csv. "
        "Ejecuta primero la auditoría para generar el dashboard."
    )
