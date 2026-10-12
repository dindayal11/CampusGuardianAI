# =========================================================
# CAMPUS GUARDIAN AI
# LOCATION RISK ANALYZER
# =========================================================


def analyze_location_risk(complaints):

    location_data = {}

    for complaint in complaints:

        # =================================================
        # CURRENT DATABASE COMPLAINT ORDER
        # =================================================
        # 0  id
        # 1  complaint_id
        # 2  institute_id
        # 3  student_id
        # 4  title
        # 5  description
        # 6  location
        # 7  category
        # 8  priority
        # 9  anonymous
        # 10 image_path
        # 11 status
        # 12 created_at
        # 13 department
        # =================================================

        location = complaint[6]
        priority = complaint[8]
        status = complaint[11]

        # Ignore empty locations
        if not location:
            continue

        location = str(location).strip()

        if not location:
            continue

        # Create location entry
        if location not in location_data:

            location_data[location] = {
                "total": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "pending": 0,
                "in_progress": 0,
                "resolved": 0,
                "rejected": 0
            }

        data = location_data[location]

        # =================================================
        # TOTAL
        # =================================================

        data["total"] += 1

        # =================================================
        # PRIORITY
        # =================================================

        if priority == "Critical":
            data["critical"] += 1

        elif priority == "High":
            data["high"] += 1

        elif priority == "Medium":
            data["medium"] += 1

        elif priority == "Low":
            data["low"] += 1

        # =================================================
        # STATUS
        # =================================================

        if status == "Pending":
            data["pending"] += 1

        elif status == "In Progress":
            data["in_progress"] += 1

        elif status == "Resolved":
            data["resolved"] += 1

        elif status == "Rejected":
            data["rejected"] += 1

    # =====================================================
    # CALCULATE LOCATION RISK
    # =====================================================

    for location, data in location_data.items():

        # Base complaint activity
        risk_score = data["total"] * 5

        # Serious complaints
        risk_score += data["critical"] * 30
        risk_score += data["high"] * 15

        # Unresolved complaints
        risk_score += data["pending"] * 5
        risk_score += data["in_progress"] * 3

        # Rejected complaints should not increase risk
        # because rejection means the complaint is not
        # currently considered an active issue.

        # Limit score
        risk_score = min(risk_score, 100)

        safety_score = 100 - risk_score

        # =================================================
        # RISK LEVEL
        # =================================================

        if risk_score >= 75:

            risk_level = "Danger"

        elif risk_score >= 50:

            risk_level = "High Risk"

        elif risk_score >= 25:

            risk_level = "Moderate"

        else:

            risk_level = "Safe"

        data["risk_score"] = risk_score
        data["safety_score"] = safety_score
        data["risk_level"] = risk_level

    return location_data


# =========================================================
# DETECT SAFETY HOTSPOTS
# =========================================================

def detect_hotspots(location_risks):

    hotspots = []

    for location, data in location_risks.items():

        if data["risk_score"] >= 50:

            hotspots.append({

                "location": location,

                "risk_score":
                    data["risk_score"],

                "risk_level":
                    data["risk_level"],

                "total_complaints":
                    data["total"],

                "critical_complaints":
                    data["critical"],

                "high_complaints":
                    data["high"],

                "pending_complaints":
                    data["pending"],

                "in_progress_complaints":
                    data["in_progress"]

            })

    # Highest risk first
    hotspots.sort(
        key=lambda x: x["risk_score"],
        reverse=True
    )

    return hotspots