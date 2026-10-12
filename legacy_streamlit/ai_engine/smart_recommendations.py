def generate_recommendations(complaints, location_risks):

    recommendations = []

    if not complaints:
        return [
            "✅ No complaints available. Campus safety status is currently clear."
        ]

    # ----------------------------------
    # 1. Critical Complaints
    # ----------------------------------

    critical_count = sum(
        1 for complaint in complaints
        if complaint[6] == "Critical"
    )

    if critical_count > 0:
        recommendations.append(
            f"🚨 {critical_count} critical complaint(s) require immediate attention."
        )

    # ----------------------------------
    # 2. Pending Complaints
    # ----------------------------------

    pending_count = sum(
        1 for complaint in complaints
        if complaint[9] == "Pending"
    )

    if pending_count >= 5:
        recommendations.append(
            f"⚠️ {pending_count} complaints are still pending. "
            "Consider assigning additional staff to reduce the backlog."
        )
    elif pending_count > 0:
        recommendations.append(
            f"⏳ {pending_count} pending complaint(s) should be reviewed."
        )

    # ----------------------------------
    # 3. High-Risk Locations
    # ----------------------------------

    for location, data in location_risks.items():

        if data["risk_score"] >= 75:

            recommendations.append(
                f"🔥 {location} is a Danger Zone "
                f"with a risk score of {data['risk_score']}/100. "
                "Immediate inspection is recommended."
            )

        elif data["risk_score"] >= 50:

            recommendations.append(
                f"⚠️ {location} has high safety risk "
                f"({data['risk_score']}/100). "
                "Schedule a safety inspection."
            )

    # ----------------------------------
    # 4. Critical + Pending Combination
    # ----------------------------------

    critical_pending = sum(
        1 for complaint in complaints
        if complaint[6] == "Critical"
        and complaint[9] == "Pending"
    )

    if critical_pending > 0:
        recommendations.append(
            f"🚨 {critical_pending} critical complaint(s) are still unresolved. "
            "These should be prioritized immediately."
        )

    # ----------------------------------
    # 5. Overall Recommendation
    # ----------------------------------

    if critical_count == 0 and pending_count == 0:

        recommendations.append(
            "✅ Campus complaint status is stable. "
            "Continue regular safety monitoring."
        )

    return recommendations