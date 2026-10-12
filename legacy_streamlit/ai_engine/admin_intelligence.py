from collections import Counter


def analyze_admin_intelligence(complaints):

    if not complaints:
        return {
            "total_complaints": 0,
            "pending_complaints": 0,
            "critical_complaints": 0,
            "resolved_complaints": 0,
            "top_category": "No Data",
            "top_location": "No Data",
            "top_department": "No Data",
            "oldest_pending_days": 0
        }

    total = len(complaints)

    pending = 0
    critical = 0
    resolved = 0

    categories = []
    locations = []

    for complaint in complaints:

        # Current database tuple order
        location = complaint[6]
        category = complaint[7]
        priority = complaint[8]
        status = complaint[11]

        categories.append(category)
        locations.append(location)

        if status == "Pending":
            pending += 1

        if priority == "Critical":
            critical += 1

        if status == "Resolved":
            resolved += 1

    top_category = (
        Counter(categories).most_common(1)[0][0]
        if categories else "No Data"
    )

    top_location = (
        Counter(locations).most_common(1)[0][0]
        if locations else "No Data"
    )

    return {
        "total_complaints": total,
        "pending_complaints": pending,
        "critical_complaints": critical,
        "resolved_complaints": resolved,
        "top_category": top_category,
        "top_location": top_location,
        "top_department": "No Data",
        "oldest_pending_days": 0
    }