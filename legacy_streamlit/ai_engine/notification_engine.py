def generate_complaint_notification(complaint):
    """Generate display-only complaint alerts without writing to the database."""
    complaint_id = complaint[1]
    location = complaint[6]
    priority = complaint[8]
    status = complaint[11]

    notifications = []

    if status == "Pending":
        notifications.append("📝 Your complaint has been submitted successfully and is waiting for review.")
    elif status == "In Progress":
        notifications.append("🔄 Your complaint is currently being processed by the concerned department.")
    elif status == "Resolved":
        notifications.append("✅ Your complaint has been resolved successfully.")
    elif status == "Rejected":
        notifications.append("❌ Your complaint has been rejected by the administrator.")
    else:
        notifications.append(f"ℹ️ Current complaint status: {status}")

    if priority == "Critical":
        notifications.append(f"🚨 Complaint {complaint_id} at {location or 'the reported location'} requires immediate attention.")
    elif priority == "High":
        notifications.append(f"⚠️ Complaint {complaint_id} should be reviewed as soon as possible.")

    return notifications
