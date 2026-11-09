
import pandas as pd


def assign_status(cpa_vs_target):
    if cpa_vs_target <= 1:
        return "Cumple"
    elif cpa_vs_target <= 1.2:
        return "Monitorear"
    else:
        return "Requiere atención"


def assign_recommendation(row):
    if row["calculated_performance_status"] == "Cumple":
        return "Mantener y evaluar un incremento gradual de presupuesto."

    if row["calculated_application_rate"] < 0.015:
        return "Revisar intención del tráfico, landing page y formulario."

    if row["calculated_approval_rate"] < 0.50:
        return "Revisar calidad del tráfico, audiencias y términos de búsqueda."

    if row["calculated_account_opening_rate"] < 0.60:
        return "Optimizar onboarding y seguimiento posterior a la aprobación."

    return "Revisar CPC, pujas, términos de búsqueda y distribución de presupuesto."


def run_audit(file_path="google_ads_audit.csv"):

    df = pd.read_csv(file_path)

    df["calculated_ctr"] = df["clicks"] / df["impressions"]
    df["calculated_cpc"] = df["spend"] / df["clicks"]
    df["calculated_application_rate"] = df["applications"] / df["clicks"]

    df["calculated_approval_rate"] = (
        df["approved_applications"] / df["applications"]
    )

    df["calculated_account_opening_rate"] = (
        df["opened_accounts"] / df["approved_applications"]
    )

    df["calculated_cpa"] = df["spend"] / df["opened_accounts"]

    df["calculated_cpa_vs_target"] = (
        df["calculated_cpa"] / df["target_cpa"]
    )

    df["calculated_performance_status"] = (
        df["calculated_cpa_vs_target"].apply(assign_status)
    )

    df["calculated_recommendation"] = df.apply(
        assign_recommendation,
        axis=1
    )

    df.to_csv("audit_results.csv", index=False)

    return df.to_dict(orient="records")
