
def analyze_campaigns(audit_results):
    """
    Analiza el rendimiento de las campañas.
    Identifica las mejores y peores por CPA.
    """

    if not audit_results:
        return {"message": "No hay campañas para analizar."}

    sorted_campaigns = sorted(
        audit_results,
        key=lambda campaign: campaign["calculated_cpa"]
    )

    best_campaigns = sorted_campaigns[:3]
    worst_campaigns = sorted_campaigns[-3:]

    average_cpa = sum(
        campaign["calculated_cpa"]
        for campaign in audit_results
    ) / len(audit_results)

    return {
        "average_cpa": average_cpa,
        "best_campaigns": best_campaigns,
        "worst_campaigns": worst_campaigns
    }



def analyze_funnel(audit_results):
    """
    Analiza el funnel por campaña y globalmente.
    Identifica:
    1. Las tres campañas con mayores pérdidas absolutas.
    2. Las tres campañas con peores tasas de conversión.
    """

    if not audit_results:
        return {"message": "No hay campañas para analizar."}

    funnel_analysis = []

    total_clicks = 0
    total_applications = 0
    total_approvals = 0
    total_openings = 0

    for campaign in audit_results:

        clicks = campaign["clicks"]
        applications = campaign["applications"]
        approvals = campaign["approved_applications"]
        openings = campaign["opened_accounts"]

        funnel_analysis.append({
            "campaign": campaign["campaign"],
            "clicks": clicks,
            "applications": applications,
            "approvals": approvals,
            "openings": openings,
            "click_to_application": campaign["calculated_application_rate"],
            "application_to_approval": campaign["calculated_approval_rate"],
            "approval_to_opening": campaign["calculated_account_opening_rate"],
            "lost_clicks_to_application": clicks - applications,
            "lost_applications_to_approval": applications - approvals,
            "lost_approvals_to_opening": approvals - openings
        })

        total_clicks += clicks
        total_applications += applications
        total_approvals += approvals
        total_openings += openings

    # Tasas globales ponderadas
    click_to_application = (
        total_applications / total_clicks
        if total_clicks else 0
    )

    application_to_approval = (
        total_approvals / total_applications
        if total_applications else 0
    )

    approval_to_opening = (
        total_openings / total_approvals
        if total_approvals else 0
    )

    # Ranking de mayores pérdidas absolutas
    top_losses = {
        "clicks_to_applications": sorted(
            funnel_analysis,
            key=lambda x: x["lost_clicks_to_application"],
            reverse=True
        )[:3],

        "applications_to_approvals": sorted(
            funnel_analysis,
            key=lambda x: x["lost_applications_to_approval"],
            reverse=True
        )[:3],

        "approvals_to_openings": sorted(
            funnel_analysis,
            key=lambda x: x["lost_approvals_to_opening"],
            reverse=True
        )[:3]
    }

    # Ranking de peores tasas de conversión
    # Solo considera campañas con datos en el denominador de cada etapa.
    worst_conversion_rates = {
        "clicks_to_applications": sorted(
            [x for x in funnel_analysis if x["clicks"] > 0],
            key=lambda x: x["click_to_application"]
        )[:3],

        "applications_to_approvals": sorted(
            [x for x in funnel_analysis if x["applications"] > 0],
            key=lambda x: x["application_to_approval"]
        )[:3],

        "approvals_to_openings": sorted(
            [x for x in funnel_analysis if x["approvals"] > 0],
            key=lambda x: x["approval_to_opening"]
        )[:3]
    }

    return {
        "campaign_analysis": funnel_analysis,

        "global_funnel": {
            "total_clicks": total_clicks,
            "total_applications": total_applications,
            "total_approvals": total_approvals,
            "total_openings": total_openings,
            "click_to_application_rate": click_to_application,
            "application_to_approval_rate": application_to_approval,
            "approval_to_opening_rate": approval_to_opening
        },

        "global_losses": {
            "clicks_to_applications": total_clicks - total_applications,
            "applications_to_approvals": total_applications - total_approvals,
            "approvals_to_openings": total_approvals - total_openings
        },

        "top_losses_by_stage": top_losses,

        "worst_conversion_rates_by_stage": worst_conversion_rates
    }
def compare_periods(september_results, october_results):
    """
    Compara el rendimiento de las campañas
    entre dos periodos.
    """

    comparisons = []

    october_campaigns = {
        campaign["campaign"]: campaign
        for campaign in october_results
    }

    for september in september_results:

        campaign_name = september["campaign"]

        if campaign_name not in october_campaigns:
            continue

        october = october_campaigns[campaign_name]

        september_cpa = (
            september["spend"] / september["opened_accounts"]
            if september["opened_accounts"] else 0
        )

        october_cpa = (
            october["spend"] / october["opened_accounts"]
            if october["opened_accounts"] else 0
        )

        cpa_change = (
            ((october_cpa - september_cpa) / september_cpa) * 100
            if september_cpa else 0
        )

        spend_change = (
            ((october["spend"] - september["spend"])
             / september["spend"]) * 100
            if september["spend"] else 0
        )

        openings_change = (
            ((october["opened_accounts"] - september["opened_accounts"])
             / september["opened_accounts"]) * 100
            if september["opened_accounts"] else 0
        )

        comparisons.append({
            "campaign": campaign_name,
            "september_cpa": september_cpa,
            "october_cpa": october_cpa,
            "cpa_change_pct": cpa_change,
            "spend_change_pct": spend_change,
            "openings_change_pct": openings_change
        })

    return comparisons
