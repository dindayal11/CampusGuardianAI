import streamlit as st
from database.database import (
    get_announcements,
    create_announcement,
    deactivate_announcement,
    delete_announcement,
    get_students_by_institute,
    get_institute_admins,
    create_notification,
    log_audit,
)
from utils.advanced_features import base_style

st.set_page_config(
    page_title="Announcements",
    page_icon="📢",
    layout="wide",
)

base_style()

role = (
    "Student"
    if st.session_state.get("student_logged_in")
    else (
        "Institute Admin"
        if st.session_state.get("institute_admin_logged_in")
        else None
    )
)

if not role:
    st.error("🔒 Please login first.")
    st.stop()

user = (
    st.session_state.student_user
    if role == "Student"
    else st.session_state.institute_admin
)

iid = user[1]
uid = user[2]

# Flash messages survive the Streamlit rerun after Publish/Delete/Archive.
if st.session_state.get("announcement_flash"):
    st.success(st.session_state["announcement_flash"])
    del st.session_state["announcement_flash"]

st.title("📢 Announcements & Broadcasts")
st.caption("Institute communication center")

# =========================================================
# PUBLISH ANNOUNCEMENT
# =========================================================

if role == "Institute Admin":

    with st.expander("➕ Publish New Announcement", expanded=True):

        with st.form(
            "announcement_form",
            clear_on_submit=False,
            enter_to_submit=True,
        ):

            title = st.text_input(
                "Title",
                placeholder="e.g. College Sports Day",
            )

            msg = st.text_area(
                "Message",
                placeholder="Write the announcement message here...",
                height=130,
            )

            col1, col2 = st.columns(2)

            with col1:
                audience = st.selectbox(
                    "Audience",
                    ["All", "Students", "Institute Admins"],
                )

            with col2:
                priority = st.selectbox(
                    "Priority",
                    ["Normal", "High", "Critical"],
                )

            expiry = st.text_input(
                "Expiry (optional)",
                placeholder="YYYY-MM-DD HH:MM:SS",
            )

            submitted = st.form_submit_button(
                "📢 Publish",
                type="primary",
                width="stretch",
            )

        if submitted:

            title = title.strip()
            msg = msg.strip()
            expiry = expiry.strip()

            if not title:
                st.error("❌ Please enter an announcement title.")

            elif not msg:
                st.error("❌ Please enter an announcement message.")

            else:

                try:

                    result = create_announcement(
                        iid,
                        title,
                        msg,
                        audience,
                        priority,
                        uid,
                        expiry or None,
                    )

                    if not result or not result.get("success"):

                        message = (
                            result.get(
                                "message",
                                "Unable to publish announcement.",
                            )
                            if isinstance(result, dict)
                            else "Unable to publish announcement."
                        )

                        st.error(f"❌ {message}")

                    else:

                        # Announcement is already saved.
                        # Notification errors must not undo the announcement.
                        notification_errors = []

                        try:

                            if audience == "Students":
                                recipients = get_students_by_institute(iid)

                            elif audience == "Institute Admins":
                                recipients = get_institute_admins(iid)

                            else:
                                recipients = (
                                    get_students_by_institute(iid)
                                    + get_institute_admins(iid)
                                )

                            for recipient in recipients:
                                try:
                                    create_notification(
                                        iid,
                                        recipient[2],
                                        "",
                                        "System Alert",
                                        f"📢 {title}",
                                        msg,
                                    )
                                except Exception as notification_error:
                                    notification_errors.append(
                                        str(notification_error)
                                    )

                        except Exception as recipient_error:
                            notification_errors.append(
                                str(recipient_error)
                            )

                        try:
                            log_audit(
                                iid,
                                uid,
                                user[6],
                                "Announcement Published",
                                "Announcement",
                                str(result["id"]),
                            )
                        except Exception:
                            pass

                        success_message = (
                            f"✅ {result.get('message', 'Announcement published successfully.')}"
                        )

                        if notification_errors:
                            success_message += (
                                " ⚠️ Some notification(s) could not be sent."
                            )

                        # Save message before rerun so it is visible after refresh.
                        st.session_state["announcement_flash"] = success_message
                        st.rerun()

                except Exception as e:

                    st.error("❌ Announcement publish failed.")
                    st.exception(e)

# =========================================================
# ACTIVE ANNOUNCEMENTS
# =========================================================

try:

    anns = get_announcements(
        iid,
        "Students" if role == "Student" else "Institute Admins",
        True,
        100,
    )

except Exception as e:

    st.error("❌ Unable to load announcements.")
    st.exception(e)
    anns = []

if not anns:
    st.info("📭 No active announcements.")

# =========================================================
# ANNOUNCEMENT LIST
# =========================================================

for announcement in anns:

    (
        aid,
        _,
        ann_title,
        ann_message,
        ann_audience,
        ann_priority,
        created_by,
        expires,
        active,
        created,
    ) = announcement

    icon = (
        "🚨"
        if ann_priority == "Critical"
        else "⚠️"
        if ann_priority == "High"
        else "📢"
    )

    with st.container(border=True):

        st.markdown(f"### {icon} {ann_title}")
        st.write(ann_message)

        expiry_text = (
            f" • Expires: {expires}"
            if expires
            else ""
        )

        st.caption(
            f"{ann_priority} • {ann_audience} • "
            f"Published: {created}{expiry_text}"
        )

        if role == "Institute Admin":

            col_a, col_b = st.columns(2)

            with col_a:

                if st.button(
                    "🗄️ Archive",
                    key=f"archive_announcement_{aid}",
                    width="stretch",
                ):

                    try:

                        if deactivate_announcement(aid, iid):

                            try:
                                log_audit(
                                    iid,
                                    uid,
                                    user[6],
                                    "Announcement Archived",
                                    "Announcement",
                                    str(aid),
                                )
                            except Exception:
                                pass

                            st.session_state["announcement_flash"] = (
                                "✅ Announcement archived successfully."
                            )
                            st.rerun()

                        else:
                            st.error(
                                "❌ Announcement could not be archived."
                            )

                    except Exception as e:

                        st.error("❌ Archive failed.")
                        st.exception(e)

            with col_b:

                confirm_key = f"confirm_delete_{aid}"

                if not st.session_state.get(confirm_key, False):

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_announcement_btn_{aid}",
                        width="stretch",
                    ):
                        st.session_state[confirm_key] = True
                        st.rerun()

                else:

                    st.warning(
                        "⚠️ Are you sure you want to permanently delete this announcement?"
                    )

                    c1, c2 = st.columns(2)

                    with c1:

                        if st.button(
                            "✅ Yes, Delete",
                            key=f"confirm_delete_yes_{aid}",
                            width="stretch",
                        ):

                            try:

                                deleted = delete_announcement(aid, iid)

                                if deleted:

                                    st.session_state.pop(
                                        confirm_key,
                                        None,
                                    )

                                    try:
                                        log_audit(
                                            iid,
                                            uid,
                                            user[6],
                                            "Announcement Deleted",
                                            "Announcement",
                                            str(aid),
                                        )
                                    except Exception:
                                        pass

                                    st.session_state["announcement_flash"] = (
                                        "🗑️ Announcement deleted successfully."
                                    )
                                    st.rerun()

                                else:
                                    st.error(
                                        "❌ Announcement could not be deleted."
                                    )

                            except Exception as e:

                                st.error("❌ Delete failed.")
                                st.exception(e)

                    with c2:

                        if st.button(
                            "Cancel",
                            key=f"cancel_delete_{aid}",
                            width="stretch",
                        ):
                            st.session_state.pop(
                                confirm_key,
                                None,
                            )
                            st.rerun()
