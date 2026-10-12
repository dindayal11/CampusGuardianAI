import sqlite3
import hashlib
import secrets
from datetime import datetime


DB_NAME = "campus_guardian.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    conn = sqlite3.connect(DB_NAME)

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ==========================================
# PASSWORD SECURITY
# ==========================================

def hash_password(password):

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(password, stored_password):

    try:

        salt, stored_hash = stored_password.split("$")

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        ).hex()

        return secrets.compare_digest(
            password_hash,
            stored_hash
        )

    except Exception:

        return False


# ==========================================
# CREATE TABLES
# ==========================================

def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------
    # INSTITUTES
    # --------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS institutes (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        institute_code TEXT UNIQUE NOT NULL,

        name TEXT NOT NULL,

        institute_type TEXT,

        email TEXT UNIQUE NOT NULL,

        phone TEXT,

        address TEXT,

        city TEXT,

        state TEXT,

        status TEXT DEFAULT 'Pending',

        created_at TEXT,

        approved_at TEXT

    )
    """)

    # --------------------------------------
    # USERS
    # --------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        institute_id INTEGER,

        user_id TEXT UNIQUE NOT NULL,

        name TEXT NOT NULL,

        email TEXT,

        password TEXT NOT NULL,

        role TEXT NOT NULL,

        status TEXT DEFAULT 'Active',

        created_at TEXT,

        last_login TEXT,

        FOREIGN KEY (institute_id)
        REFERENCES institutes(id)

    )
    """)

    # --------------------------------------
    # COMPLAINTS
    # --------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        complaint_id TEXT UNIQUE,

        institute_id INTEGER,

        student_id TEXT,

        title TEXT NOT NULL,

        description TEXT NOT NULL,

        location TEXT NOT NULL,

        category TEXT,

        priority TEXT,

        anonymous INTEGER DEFAULT 0,

        image_path TEXT,

        status TEXT DEFAULT 'Pending',

        created_at TEXT,

        FOREIGN KEY (institute_id)
        REFERENCES institutes(id)

    )
    """)
    
        # --------------------------------------
    # DEPARTMENTS
    # --------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        institute_id INTEGER NOT NULL,

        department_name TEXT NOT NULL COLLATE NOCASE,

        description TEXT,

        status TEXT DEFAULT 'Active',

        created_at TEXT,

        updated_at TEXT,

        FOREIGN KEY (institute_id)
        REFERENCES institutes(id),

        UNIQUE (
            institute_id,
            department_name
        )

    )
    """)
    
    
        # --------------------------------------
    # NOTIFICATIONS
    # --------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        institute_id INTEGER,

        user_id TEXT,

        complaint_id TEXT,

        notification_type TEXT NOT NULL,

        title TEXT NOT NULL,

        message TEXT NOT NULL,

        is_read INTEGER DEFAULT 0,

        created_at TEXT,

        FOREIGN KEY (institute_id)
        REFERENCES institutes(id)

    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notification_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        institute_id INTEGER NOT NULL,
        user_id TEXT NOT NULL,
        in_app_enabled INTEGER DEFAULT 1,
        complaint_updates INTEGER DEFAULT 1,
        priority_alerts INTEGER DEFAULT 1,
        admin_alerts INTEGER DEFAULT 1,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (institute_id) REFERENCES institutes(id),
        UNIQUE (institute_id, user_id)
    )
    """)
    
    
        # --------------------------------------
    # CAMPUS MAP SETTINGS
    # --------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS campus_map_settings (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        institute_id INTEGER UNIQUE NOT NULL,

        center_latitude REAL NOT NULL,

        center_longitude REAL NOT NULL,

        default_zoom INTEGER DEFAULT 17,

        heatmap_enabled INTEGER DEFAULT 1,

        complaint_markers_enabled INTEGER DEFAULT 1,

        hotspots_enabled INTEGER DEFAULT 1,

        campus_locations_enabled INTEGER DEFAULT 1,

        created_at TEXT,

        updated_at TEXT,

        FOREIGN KEY (institute_id)
        REFERENCES institutes(id)
    )
    """)


    # --------------------------------------
    # CAMPUS LOCATIONS
    # --------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS campus_locations (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        institute_id INTEGER NOT NULL,

        location_name TEXT NOT NULL,

        latitude REAL NOT NULL,

        longitude REAL NOT NULL,

        location_type TEXT DEFAULT 'General',

        is_active INTEGER DEFAULT 1,

        created_at TEXT,

        updated_at TEXT,

        FOREIGN KEY (institute_id)
        REFERENCES institutes(id),

        UNIQUE (
            institute_id,
            location_name
        )
    )
    """)

        # --------------------------------------
    # SAFE DATABASE MIGRATION
    # --------------------------------------

    cursor.execute("""
        PRAGMA table_info(complaints)
    """)

    complaint_columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    # --------------------------------------
    # ADD STUDENT_ID IF MISSING
    # --------------------------------------

    if "student_id" not in complaint_columns:

        cursor.execute("""
            ALTER TABLE complaints
            ADD COLUMN student_id TEXT
        """)

    # --------------------------------------
    # ADD DEPARTMENT IF MISSING
    # --------------------------------------

    if "department" not in complaint_columns:

        cursor.execute("""
            ALTER TABLE complaints
            ADD COLUMN department TEXT
        """)

    conn.commit()
    conn.close()


# ==========================================
# CAMPUS MAP SETTINGS
# ==========================================

def get_campus_map_settings(institute_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        center_latitude,
        center_longitude,
        default_zoom,
        heatmap_enabled,
        complaint_markers_enabled,
        hotspots_enabled,
        campus_locations_enabled
    FROM campus_map_settings
    WHERE institute_id = ?
    """, (
        institute_id,
    ))

    settings = cursor.fetchone()

    conn.close()

    if not settings:
        return None

    return {
        "center_latitude": settings[0],
        "center_longitude": settings[1],
        "default_zoom": settings[2],
        "heatmap_enabled": settings[3],
        "complaint_markers_enabled": settings[4],
        "hotspots_enabled": settings[5],
        "campus_locations_enabled": settings[6]
    }



def create_campus_map_settings(
    institute_id,
    center_latitude,
    center_longitude,
    default_zoom=17
):

    conn = get_connection()
    cursor = conn.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
    INSERT OR IGNORE INTO campus_map_settings (

        institute_id,
        center_latitude,
        center_longitude,
        default_zoom,
        heatmap_enabled,
        complaint_markers_enabled,
        hotspots_enabled,
        campus_locations_enabled,
        created_at,
        updated_at

    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        institute_id,
        center_latitude,
        center_longitude,
        default_zoom,
        1,
        1,
        1,
        1,
        created_at,
        created_at

    ))

    conn.commit()
    conn.close()


def update_campus_map_settings(
    institute_id,
    center_latitude,
    center_longitude,
    default_zoom,
    heatmap_enabled,
    complaint_markers_enabled,
    hotspots_enabled,
    campus_locations_enabled
):

    conn = get_connection()
    cursor = conn.cursor()

    updated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
    UPDATE campus_map_settings

    SET
        center_latitude = ?,
        center_longitude = ?,
        default_zoom = ?,
        heatmap_enabled = ?,
        complaint_markers_enabled = ?,
        hotspots_enabled = ?,
        campus_locations_enabled = ?,
        updated_at = ?

    WHERE institute_id = ?
    """, (

        center_latitude,
        center_longitude,
        default_zoom,
        heatmap_enabled,
        complaint_markers_enabled,
        hotspots_enabled,
        campus_locations_enabled,
        updated_at,
        institute_id

    ))

    conn.commit()
    conn.close()


# ==========================================
# CAMPUS LOCATIONS
# ==========================================

def get_campus_locations(institute_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        institute_id,
        location_name,
        latitude,
        longitude,
        location_type,
        is_active,
        created_at,
        updated_at
    FROM campus_locations

    WHERE institute_id = ?

    AND is_active = 1

    ORDER BY location_name
    """, (
        institute_id,
    ))

    locations = cursor.fetchall()

    conn.close()

    return [
        {
            "id": location[0],
            "institute_id": location[1],
            "location_name": location[2],
            "latitude": location[3],
            "longitude": location[4],
            "location_type": location[5],
            "is_active": location[6],
            "created_at": location[7],
            "updated_at": location[8]
        }
        for location in locations
    ]



def add_campus_location(
    institute_id,
    location_name,
    latitude,
    longitude,
    location_type="General"
):

    conn = get_connection()
    cursor = conn.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    try:

        cursor.execute("""
        INSERT INTO campus_locations (

            institute_id,
            location_name,
            latitude,
            longitude,
            location_type,
            is_active,
            created_at,
            updated_at

        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            institute_id,
            location_name.strip(),
            latitude,
            longitude,
            location_type,
            1,
            created_at,
            created_at

        ))

        conn.commit()
        conn.close()

        return True

    except Exception:

        conn.rollback()
        conn.close()

        return False


def update_campus_location(
    location_id,
    institute_id,
    location_name,
    latitude,
    longitude,
    location_type
):

    conn = get_connection()
    cursor = conn.cursor()

    updated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
    UPDATE campus_locations

    SET
        location_name = ?,
        latitude = ?,
        longitude = ?,
        location_type = ?,
        updated_at = ?

    WHERE id = ?

    AND institute_id = ?
    """, (

        location_name.strip(),
        latitude,
        longitude,
        location_type,
        updated_at,
        location_id,
        institute_id

    ))

    affected = cursor.rowcount

    conn.commit()
    conn.close()

    return affected > 0


def delete_campus_location(
    location_id,
    institute_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE campus_locations

    SET
        is_active = 0

    WHERE id = ?

    AND institute_id = ?
    """, (
        location_id,
        institute_id
    ))

    affected = cursor.rowcount

    conn.commit()
    conn.close()

    return affected > 0


# ==========================================
# CLEANUP LEGACY JBIT CAMPUS MAP
# ==========================================

def cleanup_legacy_jbit_campus_map():

    conn = get_connection()
    cursor = conn.cursor()

    # These are ONLY the old hardcoded JBIT values that were
    # created by the previous initializer. Existing/custom
    # admin-created locations are preserved.
    legacy_locations = [
        ("Main Gate", 30.37869, 77.82510),
        ("Academic Block", 30.37895, 77.82530),
        ("CSE Department", 30.37905, 77.82545),
        ("Library", 30.37885, 77.82555),
        ("Canteen", 30.37860, 77.82550),
        ("Parking Area", 30.37845, 77.82495),
        ("Hostel Block A", 30.37920, 77.82580),
        ("Playground", 30.37830, 77.82580)
    ]

    try:

        # Remove only rows that exactly match the old initializer.
        for location_name, latitude, longitude in legacy_locations:

            cursor.execute("""
            DELETE FROM campus_locations
            WHERE institute_id = ?
            AND location_name = ?
            AND latitude = ?
            AND longitude = ?
            """, (
                1,
                location_name,
                latitude,
                longitude
            ))

        # Remove the old default map-settings row ONLY when it still
        # contains the exact values created by the old initializer.
        # If an admin has already customized the map, it is preserved.
        cursor.execute("""
        DELETE FROM campus_map_settings
        WHERE institute_id = ?
        AND center_latitude = ?
        AND center_longitude = ?
        AND default_zoom = ?
        AND heatmap_enabled = 1
        AND complaint_markers_enabled = 1
        AND hotspots_enabled = 1
        AND campus_locations_enabled = 1
        """, (
            1,
            30.37869,
            77.82510,
            17
        ))

        conn.commit()

    except Exception:

        conn.rollback()

    finally:

        conn.close()


# ==========================================
# INSTITUTE CODE
# ==========================================

def generate_institute_code():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM institutes"
    )

    count = cursor.fetchone()[0] + 1

    conn.close()

    return f"INST-{count:04d}"


# ==========================================
# ADMIN USER ID
# ==========================================

def generate_admin_user_id(institute_code):

    return f"{institute_code}-ADMIN"


# ==========================================
# REGISTER INSTITUTE
# ==========================================

def register_institute(
    name,
    institute_type,
    email,
    phone,
    address,
    city,
    state,
    admin_name,
    admin_email,
    admin_password
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # ----------------------------------
        # CHECK EXISTING INSTITUTE EMAIL
        # ----------------------------------

        cursor.execute("""
        SELECT id
        FROM institutes
        WHERE email = ?
        """, (email.strip().lower(),))

        existing = cursor.fetchone()

        if existing:

            conn.close()

            return {
                "success": False,
                "message": "An institute with this email already exists."
            }

        # ----------------------------------
        # CREATE INSTITUTE
        # ----------------------------------

        institute_code = generate_institute_code()

        created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
        INSERT INTO institutes (

            institute_code,
            name,
            institute_type,
            email,
            phone,
            address,
            city,
            state,
            status,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            institute_code,
            name.strip(),
            institute_type,
            email.strip().lower(),
            phone.strip(),
            address.strip(),
            city.strip(),
            state,
            "Pending",
            created_at

        ))

        institute_id = cursor.lastrowid

        # ----------------------------------
        # CREATE ADMIN ACCOUNT
        # ----------------------------------

        admin_user_id = generate_admin_user_id(
            institute_code
        )

        hashed_password = hash_password(
            admin_password
        )

        cursor.execute("""
        INSERT INTO users (

            institute_id,
            user_id,
            name,
            email,
            password,
            role,
            status,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            institute_id,
            admin_user_id,
            admin_name.strip(),
            admin_email.strip().lower(),
            hashed_password,
            "Institute Admin",
            "Pending",
            created_at

        ))

        conn.commit()
        conn.close()

        return {

            "success": True,

            "message":
            "Institute registration submitted successfully.",

            "institute_code":
            institute_code,

            "admin_user_id":
            admin_user_id

        }

    except sqlite3.IntegrityError:

        conn.rollback()
        conn.close()

        return {

            "success": False,

            "message":
            "This email or account information is already registered."

        }

    except Exception as e:

        conn.rollback()
        conn.close()

        return {

            "success": False,

            "message":
            f"Registration failed: {e}"

        }


# ==========================================
# GET INSTITUTE BY CODE
# ==========================================

def get_institute_by_code(institute_code):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM institutes
    WHERE institute_code = ?
    """, (institute_code,))

    institute = cursor.fetchone()

    conn.close()

    return institute


# ==========================================
# GET ALL INSTITUTES
# ==========================================

def get_all_institutes():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM institutes
    ORDER BY id DESC
    """)

    institutes = cursor.fetchall()

    conn.close()

    return institutes


# ==========================================
# GET USER BY USER ID
# ==========================================

def get_user_by_id(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM users
    WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()

    conn.close()

    return user


# ==========================================
# AUTHENTICATE USER
# ==========================================

def change_user_password(user_id, *args):
    """Change a user's password; supports legacy 3-argument and institute-scoped 4-argument calls."""
    if len(args) == 2:
        current_password, new_password = args
        institute_id = None
    elif len(args) == 3:
        institute_id, current_password, new_password = args
    else:
        return {"success": False, "message": "Invalid password change arguments."}

    user_id = (user_id or "").strip()
    if not new_password or len(new_password) < 8:
        return {"success": False, "message": "New password must be at least 8 characters."}
    if current_password == new_password:
        return {"success": False, "message": "New password must be different from the current password."}

    conn = get_connection()
    cursor = conn.cursor()
    if institute_id is None:
        cursor.execute("SELECT password, institute_id FROM users WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("SELECT password, institute_id FROM users WHERE user_id = ? AND institute_id = ?", (user_id, institute_id))
    user = cursor.fetchone()
    if user is None or not verify_password(current_password, user[0]):
        conn.close()
        return {"success": False, "message": "Current password is incorrect." if user else "User account not found."}

    cursor.execute("UPDATE users SET password = ? WHERE user_id = ?" + (" AND institute_id = ?" if institute_id is not None else ""),
                   ((hash_password(new_password), user_id, institute_id) if institute_id is not None else (hash_password(new_password), user_id)))
    changed = cursor.rowcount
    conn.commit()
    conn.close()
    if changed != 1:
        return {"success": False, "message": "Password could not be updated."}
    return {"success": True, "message": "Password changed successfully."}



def authenticate_user(user_id, password):

    user = get_user_by_id(
        user_id.strip()
    )

    if user is None:

        return {
            "success": False,
            "message": "Invalid User ID or Password."
        }

    # users table indexes:
    # 0 id
    # 1 institute_id
    # 2 user_id
    # 3 name
    # 4 email
    # 5 password
    # 6 role
    # 7 status
    # 8 created_at
    # 9 last_login

    if not verify_password(
        password,
        user[5]
    ):

        return {
            "success": False,
            "message": "Invalid User ID or Password."
        }

    if user[7] != "Active":

        return {
            "success": False,
            "message":
            "Your account is not active yet."
        }

    conn = get_connection()
    cursor = conn.cursor()

    last_login = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
    UPDATE users
    SET last_login = ?
    WHERE user_id = ?
    """, (
        last_login,
        user[2]
    ))

    conn.commit()
    conn.close()

    return {

        "success": True,

        "user": user

    }


# ==========================================
# APPROVE INSTITUTE
# ==========================================

def approve_institute(institute_id):

    conn = get_connection()
    cursor = conn.cursor()

    approved_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
    UPDATE institutes
    SET status = 'Approved',
        approved_at = ?
    WHERE id = ?
    """, (
        approved_at,
        institute_id
    ))

    cursor.execute("""
    UPDATE users
    SET status = 'Active'
    WHERE institute_id = ?
    AND role = 'Institute Admin'
    """, (
        institute_id,
    ))

    conn.commit()
    conn.close()


# ==========================================
# GENERATE COMPLAINT ID
# ==========================================

def generate_complaint_id():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM complaints"
    )

    count = cursor.fetchone()[0] + 1

    conn.close()

    year = datetime.now().year

    return f"CG-{year}-{count:04d}"


## ==========================================
# ADD COMPLAINT
# ==========================================

def add_complaint(
    title,
    description,
    location,
    category,
    priority,
    anonymous,
    image_path=None,
    institute_id=None,
    student_id=None,
    department=None
):

    conn = get_connection()
    cursor = conn.cursor()

    complaint_id = generate_complaint_id()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
    INSERT INTO complaints (

        complaint_id,
        institute_id,
        student_id,
        title,
        description,
        location,
        category,
        priority,
        anonymous,
        image_path,
        status,
        created_at,
        department

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        complaint_id,
        institute_id,
        student_id,
        title,
        description,
        location,
        category,
        priority,
        anonymous,
        image_path,
        "Pending",
        created_at,
        department

    ))

    conn.commit()
    conn.close()

    return complaint_id

# ==========================================
# GET ALL COMPLAINTS
# ==========================================

def get_all_complaints(institute_id=None):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        id,
        complaint_id,
        institute_id,
        student_id,
        title,
        description,
        location,
        category,
        priority,
        anonymous,
        image_path,
        status,
        created_at,
        department
    FROM complaints
    """

    if institute_id is not None:
        query += """
        WHERE institute_id = ?
        ORDER BY id DESC
        """
        cursor.execute(query, (institute_id,))
    else:
        query += """
        ORDER BY id DESC
        """
        cursor.execute(query)

    complaints = cursor.fetchall()

    conn.close()

    return complaints
# ==========================================
# GET COMPLAINT BY ID
# ==========================================

def get_complaint_by_id(
    complaint_id,
    institute_id=None
):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        id,
        complaint_id,
        institute_id,
        student_id,
        title,
        description,
        location,
        category,
        priority,
        anonymous,
        image_path,
        status,
        created_at,
        department
    FROM complaints
    WHERE complaint_id = ?
    """

    if institute_id is not None:
        query += """
        AND institute_id = ?
        """

        cursor.execute(
            query,
            (complaint_id, institute_id)
        )

    else:

        cursor.execute(
            query,
            (complaint_id,)
        )

    complaint = cursor.fetchone()

    conn.close()

    return complaint


# ==========================================
# GET COMPLAINTS BY STUDENT
# ==========================================

def get_complaints_by_student(
    student_id,
    institute_id=None
):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        id,
        complaint_id,
        institute_id,
        student_id,
        title,
        description,
        location,
        category,
        priority,
        anonymous,
        image_path,
        status,
        created_at
    FROM complaints
    WHERE student_id = ?
    """

    if institute_id is not None:

        query += """
        AND institute_id = ?
        ORDER BY id DESC
        """

        cursor.execute(
            query,
            (student_id, institute_id)
        )

    else:

        query += """
        ORDER BY id DESC
        """

        cursor.execute(
            query,
            (student_id,)
        )

    complaints = cursor.fetchall()

    conn.close()

    return complaints

# ==========================================
# UPDATE COMPLAINT STATUS
# ==========================================

def update_complaint_status(
    complaint_id,
    new_status,
    institute_id=None
):

    conn = get_connection()
    cursor = conn.cursor()

    if institute_id is None:

        cursor.execute("""
        UPDATE complaints
        SET status = ?
        WHERE complaint_id = ?
        """, (
            new_status,
            complaint_id
        ))

    else:

        cursor.execute("""
        UPDATE complaints
        SET status = ?
        WHERE complaint_id = ?
        AND institute_id = ?
        """, (
            new_status,
            complaint_id,
            institute_id
        ))

    conn.commit()
    conn.close()

# ==========================================
# UPDATE COMPLAINT DEPARTMENT
# ==========================================

def update_complaint_department(
    complaint_id,
    department,
    institute_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE complaints
    SET department = ?
    WHERE complaint_id = ?
    AND institute_id = ?
    """, (
        department,
        complaint_id,
        institute_id
    ))

    conn.commit()
    conn.close()

# ==========================================
# COMPLAINT STATISTICS
# ==========================================

def get_complaint_stats(institute_id=None):

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------
    # TOTAL
    # --------------------------------------

    if institute_id is None:

        cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        """)

    else:

        cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE institute_id = ?
        """, (institute_id,))

    total = cursor.fetchone()[0]

    # --------------------------------------
    # PENDING
    # --------------------------------------

    if institute_id is None:

        cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Pending'
        """)

    else:

        cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Pending'
        AND institute_id = ?
        """, (institute_id,))

    pending = cursor.fetchone()[0]

    # --------------------------------------
    # CRITICAL
    # --------------------------------------

    if institute_id is None:

        cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE priority = 'Critical'
        """)

    else:

        cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE priority = 'Critical'
        AND institute_id = ?
        """, (institute_id,))

    critical = cursor.fetchone()[0]

    # --------------------------------------
    # RESOLVED
    # --------------------------------------

    if institute_id is None:

        cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Resolved'
        """)

    else:

        cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Resolved'
        AND institute_id = ?
        """, (institute_id,))

    resolved = cursor.fetchone()[0]

    conn.close()

    return {

        "total": total,

        "pending": pending,

        "critical": critical,

        "resolved": resolved

    }


# ==========================================
# DUPLICATE CHECK
# ==========================================

def get_complaints_for_duplicate_check(
    institute_id=None
):

    conn = get_connection()
    cursor = conn.cursor()

    if institute_id is None:

        cursor.execute("""
        SELECT *
        FROM complaints
        ORDER BY id DESC
        """)

    else:

        cursor.execute("""
        SELECT *
        FROM complaints
        WHERE institute_id = ?
        ORDER BY id DESC
        """, (institute_id,))

    complaints = cursor.fetchall()

    conn.close()

    return complaints


# ==========================================
# PLATFORM ADMIN
# ==========================================

def create_platform_admin():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS platform_admins (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        admin_id TEXT UNIQUE NOT NULL,

        name TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        status TEXT DEFAULT 'Active',

        created_at TEXT DEFAULT CURRENT_TIMESTAMP

    )
    """)

    cursor.execute(
        "SELECT id FROM platform_admins WHERE email = ?",
        ("admin@campusguardian.ai",)
    )

    existing_admin = cursor.fetchone()

    if not existing_admin:

        password_hash = hash_password(
            "Admin@123"
        )

        cursor.execute("""
        INSERT INTO platform_admins
        (
            admin_id,
            name,
            email,
            password,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """, (

            "PLATFORM-ADMIN-001",
            "Platform Administrator",
            "admin@campusguardian.ai",
            password_hash,
            "Active"

        ))

    conn.commit()
    conn.close()


# ==========================================
# AUTHENTICATE PLATFORM ADMIN
# ==========================================

def change_platform_admin_password(email, current_password, new_password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM platform_admins
    WHERE email = ?
    """, (email.strip().lower(),))

    admin = cursor.fetchone()

    if admin is None:
        conn.close()
        return {
            "success": False,
            "message": "Platform admin account not found."
        }

    if admin[5] != "Active":
        conn.close()
        return {
            "success": False,
            "message": "Platform admin account is not active."
        }

    if not verify_password(current_password, admin[4]):
        conn.close()
        return {
            "success": False,
            "message": "Current password is incorrect."
        }

    if current_password == new_password:
        conn.close()
        return {
            "success": False,
            "message": "New password must be different from the current password."
        }

    cursor.execute("""
    UPDATE platform_admins
    SET password = ?
    WHERE email = ?
    """, (
        hash_password(new_password),
        email.strip().lower()
    ))

    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed != 1:
        return {
            "success": False,
            "message": "Password could not be updated."
        }

    return {
        "success": True,
        "message": "Password changed successfully."
    }


def authenticate_platform_admin(
    email,
    password
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS platform_admins (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        admin_id TEXT UNIQUE NOT NULL,

        name TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        status TEXT DEFAULT 'Active',

        created_at TEXT DEFAULT CURRENT_TIMESTAMP

    )
    """)

    cursor.execute("""
    SELECT *
    FROM platform_admins
    WHERE email = ?
    """, (
        email.strip().lower(),
    ))

    admin = cursor.fetchone()

    conn.commit()
    conn.close()

    if not admin:

        return None

    if admin[5] != "Active":

        return None

    if verify_password(
        password,
        admin[4]
    ):

        return admin

    return None


# ==========================================
# GET PENDING INSTITUTES
# ==========================================

def get_pending_institutes():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM institutes
    WHERE status = 'Pending'
    ORDER BY created_at DESC
    """)

    institutes = cursor.fetchall()

    conn.close()

    return institutes


# ==========================================
# REJECT INSTITUTE
# ==========================================

def reject_institute(institute_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE institutes
    SET status = 'Rejected'
    WHERE id = ?
    """, (
        institute_id,
    ))

    cursor.execute("""
    UPDATE users
    SET status = 'Rejected'
    WHERE institute_id = ?
    AND role = 'Institute Admin'
    """, (
        institute_id,
    ))

    conn.commit()
    conn.close()

    return True


# ==========================================
# BLOCK INSTITUTE
# ==========================================

def block_institute(institute_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE institutes
    SET status = 'Blocked'
    WHERE id = ?
    """, (
        institute_id,
    ))

    cursor.execute("""
    UPDATE users
    SET status = 'Blocked'
    WHERE institute_id = ?
    """, (
        institute_id,
    ))

    conn.commit()
    conn.close()

    return True


# ==========================================
# STUDENT MANAGEMENT
# ==========================================

def generate_student_user_id(institute_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT institute_code
    FROM institutes
    WHERE id = ?
    """, (
        institute_id,
    ))

    institute = cursor.fetchone()

    if not institute:

        conn.close()

        return None

    institute_code = institute[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM users
    WHERE institute_id = ?
    AND role = 'Student'
    """, (
        institute_id,
    ))

    count = cursor.fetchone()[0] + 1

    conn.close()

    return f"{institute_code}-STU-{count:04d}"


# ==========================================
# ADD STUDENT
# ==========================================

def add_student(
    institute_id,
    name,
    email,
    password
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # ----------------------------------
        # CHECK INSTITUTE
        # ----------------------------------

        cursor.execute("""
        SELECT id, status
        FROM institutes
        WHERE id = ?
        """, (
            institute_id,
        ))

        institute = cursor.fetchone()

        if not institute:

            conn.close()

            return {
                "success": False,
                "message": "Institute not found."
            }

        if institute[1] != "Approved":

            conn.close()

            return {
                "success": False,
                "message": "Institute is not approved."
            }

        # ----------------------------------
        # CHECK EMAIL
        # ----------------------------------

        if email:

            cursor.execute("""
            SELECT id
            FROM users
            WHERE email = ?
            """, (
                email.strip().lower(),
            ))

            existing = cursor.fetchone()

            if existing:

                conn.close()

                return {
                    "success": False,
                    "message":
                    "This email is already registered."
                }

        # ----------------------------------
        # GENERATE STUDENT ID
        # ----------------------------------

        student_id = generate_student_user_id(
            institute_id
        )

        # ----------------------------------
        # HASH PASSWORD
        # ----------------------------------

        hashed_password = hash_password(
            password
        )

        created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # ----------------------------------
        # CREATE STUDENT
        # ----------------------------------

        cursor.execute("""
        INSERT INTO users (

            institute_id,
            user_id,
            name,
            email,
            password,
            role,
            status,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            institute_id,
            student_id,
            name.strip(),
            email.strip().lower()
            if email else None,
            hashed_password,
            "Student",
            "Active",
            created_at

        ))

        conn.commit()
        conn.close()

        return {

            "success": True,

            "message":
            "Student account created successfully.",

            "student_id":
            student_id

        }

    except sqlite3.IntegrityError:

        conn.rollback()
        conn.close()

        return {

            "success": False,

            "message":
            "Student account could not be created. "
            "The information may already exist."

        }

    except Exception as e:

        conn.rollback()
        conn.close()

        return {

            "success": False,

            "message":
            f"Student creation failed: {e}"

        }


# ==========================================
# GET STUDENTS BY INSTITUTE
# ==========================================

def get_students_by_institute(
    institute_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        institute_id,
        user_id,
        name,
        email,
        role,
        status,
        created_at,
        last_login
    FROM users
    WHERE institute_id = ?
    AND role = 'Student'
    ORDER BY id DESC
    """, (
        institute_id,
    ))

    students = cursor.fetchall()

    conn.close()

    return students


# ==========================================
# UPDATE STUDENT STATUS
# ==========================================

def update_student_status(
    student_id,
    status,
    institute_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET status = ?
    WHERE user_id = ?
    AND institute_id = ?
    AND role = 'Student'
    """, (
        status,
        student_id,
        institute_id
    ))

    affected = cursor.rowcount

    conn.commit()
    conn.close()

    return affected > 0



# =========================================================
# DEPARTMENT MANAGEMENT
# =========================================================

def create_department(institute_id, department_name, description=""):
    """
    Create a new department for an institute.
    """

    department_name = department_name.strip()
    description = description.strip()

    if not department_name:
        return {
            "success": False,
            "message": "Department name is required."
        }

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check institute
        cursor.execute("""
            SELECT id, status
            FROM institutes
            WHERE id = ?
        """, (institute_id,))

        institute = cursor.fetchone()

        if not institute:
            return {
                "success": False,
                "message": "Institute not found."
            }

        if institute[1] != "Approved":
            return {
                "success": False,
                "message": "Institute is not approved."
            }

        # Check duplicate department
        cursor.execute("""
            SELECT id
            FROM departments
            WHERE institute_id = ?
            AND department_name = ?
        """, (institute_id, department_name))

        existing = cursor.fetchone()

        if existing:
            return {
                "success": False,
                "message": "Department with this name already exists."
            }

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO departments (
                institute_id,
                department_name,
                description,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            institute_id,
            department_name,
            description,
            "Active",
            now,
            now
        ))

        conn.commit()

        return {
            "success": True,
            "message": "Department created successfully."
        }

    except Exception as e:
        conn.rollback()

        return {
            "success": False,
            "message": f"Failed to create department: {e}"
        }

    finally:
        conn.close()


def get_departments_by_institute(institute_id):
    """
    Get all departments belonging to one institute.
    """

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            institute_id,
            department_name,
            description,
            status,
            created_at,
            updated_at
        FROM departments
        WHERE institute_id = ?
        ORDER BY id DESC
    """, (institute_id,))

    departments = cursor.fetchall()

    conn.close()

    return departments


def update_department(
    department_id,
    department_name,
    description,
    institute_id
):
    """
    Update a department.
    Institute isolation is enforced.
    """

    department_name = department_name.strip()
    description = description.strip()

    if not department_name:
        return {
            "success": False,
            "message": "Department name is required."
        }

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check department belongs to this institute
        cursor.execute("""
            SELECT id
            FROM departments
            WHERE id = ?
            AND institute_id = ?
        """, (
            department_id,
            institute_id
        ))

        department = cursor.fetchone()

        if not department:
            return {
                "success": False,
                "message": "Department not found."
            }

        # Check duplicate name
        cursor.execute("""
            SELECT id
            FROM departments
            WHERE institute_id = ?
            AND department_name = ?
            AND id != ?
        """, (
            institute_id,
            department_name,
            department_id
        ))

        existing = cursor.fetchone()

        if existing:
            return {
                "success": False,
                "message": "Another department with this name already exists."
            }

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            UPDATE departments
            SET
                department_name = ?,
                description = ?,
                updated_at = ?
            WHERE id = ?
            AND institute_id = ?
        """, (
            department_name,
            description,
            now,
            department_id,
            institute_id
        ))

        conn.commit()

        return {
            "success": True,
            "message": "Department updated successfully."
        }

    except Exception as e:
        conn.rollback()

        return {
            "success": False,
            "message": f"Failed to update department: {e}"
        }

    finally:
        conn.close()


def update_department_status(
    department_id,
    status,
    institute_id
):
    """
    Activate or deactivate a department.
    """

    allowed_statuses = ["Active", "Inactive"]

    if status not in allowed_statuses:
        return {
            "success": False,
            "message": "Invalid department status."
        }

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE departments
            SET
                status = ?,
                updated_at = ?
            WHERE id = ?
            AND institute_id = ?
        """, (
            status,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            department_id,
            institute_id
        ))

        conn.commit()

        if cursor.rowcount == 0:
            return {
                "success": False,
                "message": "Department not found."
            }

        return {
            "success": True,
            "message": f"Department {status.lower()} successfully."
        }

    except Exception as e:
        conn.rollback()

        return {
            "success": False,
            "message": f"Failed to update department status: {e}"
        }

    finally:
        conn.close()
        
        
# =========================================================
# GET INSTITUTE ADMINS
# =========================================================

def get_institute_admins(
    institute_id
):
    """
    Get active Institute Admin users belonging to one institute.
    Institute isolation is enforced by institute_id.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            institute_id,
            user_id,
            name,
            email,
            role,
            status
        FROM users
        WHERE institute_id = ?
        AND role = 'Institute Admin'
        AND status = 'Active'
        ORDER BY id
    """, (
        institute_id,
    ))

    admins = cursor.fetchall()

    conn.close()

    return admins


# =========================================================
# NOTIFICATION MANAGEMENT
# =========================================================


def _notification_preference_column(notification_type):
    if notification_type in {"Critical Alert", "Priority Alert", "High Priority"}:
        return "priority_alerts"
    if notification_type in {"New Complaint", "Admin Alert", "System Alert", "Duplicate Alert"}:
        return "admin_alerts"
    return "complaint_updates"


def get_notification_preferences(user_id, institute_id):
    defaults = {
        "in_app_enabled": 1,
        "complaint_updates": 1,
        "priority_alerts": 1,
        "admin_alerts": 1,
    }
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT in_app_enabled, complaint_updates, priority_alerts, admin_alerts
        FROM notification_preferences
        WHERE user_id = ? AND institute_id = ?
    """, (user_id, institute_id))
    row = cursor.fetchone()
    if row is None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT OR IGNORE INTO notification_preferences
            (institute_id, user_id, in_app_enabled, complaint_updates,
             priority_alerts, admin_alerts, created_at, updated_at)
            VALUES (?, ?, 1, 1, 1, 1, ?, ?)
        """, (institute_id, user_id, now, now))
        conn.commit()
        row = (1, 1, 1, 1)
    conn.close()
    return {
        "in_app_enabled": int(row[0]),
        "complaint_updates": int(row[1]),
        "priority_alerts": int(row[2]),
        "admin_alerts": int(row[3]),
    }


def update_notification_preferences(user_id, institute_id, in_app_enabled, complaint_updates, priority_alerts, admin_alerts):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO notification_preferences
        (institute_id, user_id, in_app_enabled, complaint_updates,
         priority_alerts, admin_alerts, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(institute_id, user_id) DO UPDATE SET
            in_app_enabled = excluded.in_app_enabled,
            complaint_updates = excluded.complaint_updates,
            priority_alerts = excluded.priority_alerts,
            admin_alerts = excluded.admin_alerts,
            updated_at = excluded.updated_at
    """, (institute_id, user_id, int(bool(in_app_enabled)),
          int(bool(complaint_updates)), int(bool(priority_alerts)),
          int(bool(admin_alerts)), now, now))
    conn.commit()
    conn.close()
    return True


def create_notification(institute_id, user_id, complaint_id, notification_type, title, message):
    preferences = get_notification_preferences(user_id, institute_id)
    if not preferences["in_app_enabled"]:
        return False
    preference_column = _notification_preference_column(notification_type)
    if not preferences.get(preference_column, 1):
        return False
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO notifications
        (institute_id, user_id, complaint_id, notification_type, title, message, is_read, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 0, ?)
    """, (institute_id, user_id, complaint_id, notification_type, title, message, created_at))
    conn.commit()
    conn.close()
    return True


def get_notifications(user_id, institute_id, unread_only=False, notification_type=None, limit=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT id, institute_id, user_id, complaint_id, notification_type,
               title, message, is_read, created_at
        FROM notifications
        WHERE user_id = ? AND institute_id = ?
    """
    params = [user_id, institute_id]
    if unread_only:
        query += " AND is_read = 0"
    if notification_type and notification_type != "All":
        query += " AND notification_type = ?"
        params.append(notification_type)
    query += " ORDER BY id DESC"
    if limit is not None:
        try:
            query += " LIMIT ?"
            params.append(max(1, min(int(limit), 200)))
        except (TypeError, ValueError):
            pass
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_unread_notification_count(user_id, institute_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM notifications
        WHERE user_id = ? AND institute_id = ? AND is_read = 0
    """, (user_id, institute_id))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def mark_notification_as_read(notification_id, user_id, institute_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications SET is_read = 1
        WHERE id = ? AND user_id = ? AND institute_id = ?
    """, (notification_id, user_id, institute_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def mark_all_notifications_as_read(user_id, institute_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications SET is_read = 1
        WHERE user_id = ? AND institute_id = ? AND is_read = 0
    """, (user_id, institute_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected


def delete_notification(notification_id, user_id, institute_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM notifications
        WHERE id = ? AND user_id = ? AND institute_id = ?
    """, (notification_id, user_id, institute_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def clear_read_notifications(user_id, institute_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM notifications
        WHERE user_id = ? AND institute_id = ? AND is_read = 1
    """, (user_id, institute_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected

# ==========================================
# INITIALIZE DATABASE
# ==========================================

create_tables()
cleanup_legacy_jbit_campus_map()



def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_audit(institute_id, actor_user_id, actor_role, action, entity_type=None, entity_id=None, details=None):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""INSERT INTO audit_logs(institute_id, actor_user_id, actor_role, action, entity_type, entity_id, details, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (institute_id, actor_user_id, actor_role, action, entity_type, entity_id, details, _now()))
    conn.commit(); conn.close()

def get_audit_logs(institute_id=None, limit=200):
    conn=get_connection(); cur=conn.cursor()
    if institute_id is None:
        cur.execute("SELECT id,institute_id,actor_user_id,actor_role,action,entity_type,entity_id,details,created_at FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
    else:
        cur.execute("SELECT id,institute_id,actor_user_id,actor_role,action,entity_type,entity_id,details,created_at FROM audit_logs WHERE institute_id=? ORDER BY id DESC LIMIT ?", (institute_id,limit))
    rows=cur.fetchall(); conn.close(); return rows

def get_user_profile(user_id, institute_id):
    conn=get_connection(); cur=conn.cursor()
    cur.execute("SELECT phone,department,designation,address,emergency_contact,bio,updated_at FROM user_profiles WHERE user_id=? AND institute_id=?", (user_id,institute_id))
    row=cur.fetchone(); conn.close(); return row

def upsert_user_profile(user_id, institute_id, phone='', department='', designation='', address='', emergency_contact='', bio=''):
    conn=get_connection(); cur=conn.cursor(); now=_now()
    cur.execute("""INSERT INTO user_profiles(institute_id,user_id,phone,department,designation,address,emergency_contact,bio,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(institute_id,user_id) DO UPDATE SET phone=excluded.phone,department=excluded.department,designation=excluded.designation,address=excluded.address,emergency_contact=excluded.emergency_contact,bio=excluded.bio,updated_at=excluded.updated_at""",
                (institute_id,user_id,phone.strip(),department.strip(),designation.strip(),address.strip(),emergency_contact.strip(),bio.strip(),now))
    conn.commit(); conn.close(); return True

def create_announcement(institute_id, title, message, audience='All', priority='Normal', created_by=None, expires_at=None):
    if not title.strip() or not message.strip(): return {'success':False,'message':'Title and message are required.'}
    conn=get_connection(); cur=conn.cursor()
    cur.execute("""INSERT INTO announcements(institute_id,title,message,audience,priority,created_by,expires_at,is_active,created_at)
                   VALUES(?,?,?,?,?,?,?,1,?)""", (institute_id,title.strip(),message.strip(),audience,priority,created_by,expires_at,_now()))
    ann_id=cur.lastrowid; conn.commit(); conn.close()
    return {'success':True,'id':ann_id,'message':'Announcement published successfully.'}

def get_announcements(institute_id, audience='All', active_only=True, limit=100):
    conn=get_connection(); cur=conn.cursor(); now=_now()
    q="SELECT id,institute_id,title,message,audience,priority,created_by,expires_at,is_active,created_at FROM announcements WHERE institute_id=?"
    args=[institute_id]
    if active_only: q += " AND is_active=1 AND (expires_at IS NULL OR expires_at='' OR expires_at>=?)"; args.append(now)
    if audience and audience != 'All': q += " AND (audience='All' OR audience=?)"; args.append(audience)
    q += " ORDER BY id DESC LIMIT ?"; args.append(limit)
    cur.execute(q,args); rows=cur.fetchall(); conn.close(); return rows

def deactivate_announcement(announcement_id, institute_id):
    conn=get_connection(); cur=conn.cursor(); cur.execute("UPDATE announcements SET is_active=0 WHERE id=? AND institute_id=?",(announcement_id,institute_id)); ok=cur.rowcount>0; conn.commit(); conn.close(); return ok


def delete_announcement(announcement_id, institute_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM announcements WHERE id=? AND institute_id=?",
        (announcement_id, institute_id)
    )

    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()

    return deleted


def get_or_create_complaint_workflow(complaint_id, institute_id=None, sla_hours=48):
    conn=get_connection(); cur=conn.cursor(); cur.execute("SELECT id,complaint_id,assigned_to,sla_hours,due_at,escalation_level,resolution_notes,resolved_at,feedback_rating,feedback_comment,feedback_at,updated_at FROM complaint_workflow WHERE complaint_id=?",(complaint_id,)); row=cur.fetchone()
    if row: conn.close(); return row
    due=(datetime.now()).timestamp()+sla_hours*3600
    due_at=datetime.fromtimestamp(due).strftime('%Y-%m-%d %H:%M:%S')
    cur.execute("INSERT INTO complaint_workflow(complaint_id,sla_hours,due_at,updated_at) VALUES(?,?,?,?)",(complaint_id,sla_hours,due_at,_now())); conn.commit(); cur.execute("SELECT id,complaint_id,assigned_to,sla_hours,due_at,escalation_level,resolution_notes,resolved_at,feedback_rating,feedback_comment,feedback_at,updated_at FROM complaint_workflow WHERE complaint_id=?",(complaint_id,)); row=cur.fetchone(); conn.close(); return row

def get_complaint_workflow(complaint_id, institute_id=None):
    return get_or_create_complaint_workflow(complaint_id, institute_id)

def update_complaint_workflow(complaint_id, institute_id, assigned_to=None, sla_hours=None, escalation_level=None, resolution_notes=None):
    conn=get_connection(); cur=conn.cursor(); cur.execute("SELECT id FROM complaints WHERE complaint_id=? AND institute_id=?",(complaint_id,institute_id));
    if not cur.fetchone(): conn.close(); return False
    row=get_or_create_complaint_workflow(complaint_id,institute_id)
    _,_,old_assigned,old_sla,_,old_esc,old_notes,*_=row
    assigned_to = old_assigned if assigned_to is None else assigned_to
    sla_hours = old_sla if sla_hours is None else int(sla_hours)
    escalation_level = old_esc if escalation_level is None else int(escalation_level)
    resolution_notes = old_notes if resolution_notes is None else resolution_notes
    due_at=datetime.fromtimestamp(datetime.now().timestamp()+sla_hours*3600).strftime('%Y-%m-%d %H:%M:%S')
    cur.execute("UPDATE complaint_workflow SET assigned_to=?,sla_hours=?,due_at=?,escalation_level=?,resolution_notes=?,updated_at=? WHERE complaint_id=?",(assigned_to,sla_hours,due_at,escalation_level,resolution_notes,_now(),complaint_id))
    conn.commit(); conn.close(); return True

def mark_complaint_resolved(complaint_id, institute_id, resolution_notes=''):
    conn=get_connection(); cur=conn.cursor(); now=_now()
    cur.execute("UPDATE complaints SET status='Resolved' WHERE complaint_id=? AND institute_id=?",(complaint_id,institute_id))
    if not cur.rowcount: conn.close(); return False
    cur.execute("INSERT OR IGNORE INTO complaint_workflow(complaint_id,sla_hours,due_at,updated_at) VALUES(?,?,?,?)",(complaint_id,48,now,now))
    cur.execute("UPDATE complaint_workflow SET resolution_notes=?,resolved_at=?,updated_at=? WHERE complaint_id=?",(resolution_notes,now,now,complaint_id))
    conn.commit(); conn.close(); return True

def submit_complaint_feedback(complaint_id, institute_id, student_id, rating, comment=''):
    if int(rating) < 1 or int(rating) > 5: return False
    conn=get_connection(); cur=conn.cursor(); cur.execute("SELECT student_id,status FROM complaints WHERE complaint_id=? AND institute_id=?",(complaint_id,institute_id)); row=cur.fetchone()
    if not row or row[0] != student_id or row[1] != 'Resolved': conn.close(); return False
    now=_now(); cur.execute("INSERT OR IGNORE INTO complaint_workflow(complaint_id,sla_hours,due_at,updated_at) VALUES(?,?,?,?)",(complaint_id,48,now,now))
    cur.execute("UPDATE complaint_workflow SET feedback_rating=?,feedback_comment=?,feedback_at=?,updated_at=? WHERE complaint_id=?",(int(rating),comment.strip(),now,now,complaint_id)); conn.commit(); conn.close(); return True

def get_sla_summary(institute_id):
    conn=get_connection(); cur=conn.cursor(); now=_now()
    cur.execute("""SELECT COUNT(*), SUM(CASE WHEN cw.due_at < ? AND c.status NOT IN ('Resolved','Rejected') THEN 1 ELSE 0 END), AVG(CASE WHEN c.status='Resolved' AND cw.resolved_at IS NOT NULL THEN (julianday(cw.resolved_at)-julianday(c.created_at))*24.0 END)
                   FROM complaints c LEFT JOIN complaint_workflow cw ON cw.complaint_id=c.complaint_id WHERE c.institute_id=?""",(now,institute_id)); row=cur.fetchone(); conn.close(); return {'total':row[0] or 0,'overdue':row[1] or 0,'avg_resolution_hours':round(row[2],2) if row[2] is not None else 0}

def get_complaint_history(complaint_id, institute_id):
    conn=get_connection(); cur=conn.cursor(); cur.execute("SELECT id,actor_user_id,action,old_value,new_value,note,created_at FROM complaint_history WHERE complaint_id=? AND institute_id=? ORDER BY id DESC",(complaint_id,institute_id)); rows=cur.fetchall(); conn.close(); return rows

def add_complaint_history(institute_id, complaint_id, actor_user_id, action, old_value=None, new_value=None, note=None):
    conn=get_connection(); cur=conn.cursor(); cur.execute("INSERT INTO complaint_history(institute_id,complaint_id,actor_user_id,action,old_value,new_value,note,created_at) VALUES(?,?,?,?,?,?,?,?)",(institute_id,complaint_id,actor_user_id,action,old_value,new_value,note,_now())); conn.commit(); conn.close()

def get_institute_report_data(institute_id):
    conn=get_connection(); cur=conn.cursor()
    cur.execute("""SELECT complaint_id,title,location,category,priority,status,department,created_at,student_id FROM complaints WHERE institute_id=? ORDER BY id DESC""",(institute_id,)); rows=cur.fetchall(); conn.close(); return rows

def get_institute_overview(institute_id):
    conn=get_connection(); cur=conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE institute_id=? AND role='Student'",(institute_id,)); students=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE institute_id=? AND role='Institute Admin'",(institute_id,)); admins=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM departments WHERE institute_id=?",(institute_id,)); departments=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM complaints WHERE institute_id=?",(institute_id,)); complaints=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM complaints WHERE institute_id=? AND status='Resolved'",(institute_id,)); resolved=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM complaints WHERE institute_id=? AND priority='Critical'",(institute_id,)); critical=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM complaints WHERE institute_id=? AND priority='High'",(institute_id,)); high=cur.fetchone()[0]
    conn.close(); return {'students':students,'admins':admins,'departments':departments,'complaints':complaints,'resolved':resolved,'critical':critical,'high':high}

def get_platform_overview():
    conn=get_connection(); cur=conn.cursor();
    out={}
    for key,q in [('institutes',"SELECT COUNT(*) FROM institutes"),('approved_institutes',"SELECT COUNT(*) FROM institutes WHERE status='Approved'"),('students',"SELECT COUNT(*) FROM users WHERE role='Student'"),('admins',"SELECT COUNT(*) FROM users WHERE role='Institute Admin'"),('complaints',"SELECT COUNT(*) FROM complaints"),('resolved',"SELECT COUNT(*) FROM complaints WHERE status='Resolved'"),('pending',"SELECT COUNT(*) FROM complaints WHERE status='Pending'"),('critical',"SELECT COUNT(*) FROM complaints WHERE priority='Critical'")]:
        cur.execute(q); out[key]=cur.fetchone()[0]
    conn.close(); return out


# ==========================================
# COMPATIBILITY SCHEMA / PHASE 11-20 SUPPORT
# ==========================================

def _ensure_compatibility_schema():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS complaint_workflow (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT UNIQUE NOT NULL,
        assigned_to TEXT,
        sla_hours INTEGER DEFAULT 48,
        due_at TEXT,
        escalation_level INTEGER DEFAULT 0,
        resolution_notes TEXT,
        resolved_at TEXT,
        feedback_rating INTEGER,
        feedback_comment TEXT,
        feedback_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id)
    );
    CREATE TABLE IF NOT EXISTS complaint_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        institute_id INTEGER,
        complaint_id TEXT NOT NULL,
        actor_user_id TEXT,
        action TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT,
        note TEXT,
        created_at TEXT,
        FOREIGN KEY (institute_id) REFERENCES institutes(id)
    );
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        institute_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        audience TEXT DEFAULT 'All',
        priority TEXT DEFAULT 'Normal',
        created_by TEXT,
        expires_at TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT,
        FOREIGN KEY (institute_id) REFERENCES institutes(id)
    );
    CREATE TABLE IF NOT EXISTS user_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        institute_id INTEGER NOT NULL,
        user_id TEXT NOT NULL,
        phone TEXT,
        department TEXT,
        designation TEXT,
        address TEXT,
        emergency_contact TEXT,
        bio TEXT,
        updated_at TEXT,
        FOREIGN KEY (institute_id) REFERENCES institutes(id),
        UNIQUE(institute_id, user_id)
    );
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        institute_id INTEGER,
        actor_user_id TEXT,
        actor_role TEXT,
        action TEXT NOT NULL,
        entity_type TEXT,
        entity_id TEXT,
        details TEXT,
        created_at TEXT,
        FOREIGN KEY (institute_id) REFERENCES institutes(id)
    );
    CREATE TABLE IF NOT EXISTS platform_settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        platform_name TEXT DEFAULT 'Campus Guardian AI',
        support_email TEXT DEFAULT '',
        maintenance_mode INTEGER DEFAULT 0,
        updated_at TEXT
    );
    """)
    conn.commit()
    conn.close()


def get_audit_metrics(institute_id=None):
    conn = get_connection(); cur = conn.cursor()
    if institute_id is None:
        cur.execute("SELECT COUNT(*) FROM audit_logs"); total = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM audit_logs WHERE date(created_at)=date('now')"); today = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(DISTINCT actor_user_id) FROM audit_logs WHERE actor_user_id IS NOT NULL"); actors = cur.fetchone()[0] or 0
    else:
        cur.execute("SELECT COUNT(*) FROM audit_logs WHERE institute_id=?", (institute_id,)); total = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM audit_logs WHERE institute_id=? AND date(created_at)=date('now')", (institute_id,)); today = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(DISTINCT actor_user_id) FROM audit_logs WHERE institute_id=? AND actor_user_id IS NOT NULL", (institute_id,)); actors = cur.fetchone()[0] or 0
    if institute_id is None:
        cur.execute("SELECT COUNT(*) FROM audit_logs WHERE datetime(created_at) >= datetime('now', '-24 hours')")
        last_24h = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM audit_logs WHERE datetime(created_at) >= datetime('now', '-7 days')")
        last_7d = cur.fetchone()[0] or 0
        cur.execute("""SELECT COUNT(*) FROM audit_logs
                       WHERE (LOWER(action) LIKE '%failed%login%'
                              OR LOWER(action) LIKE '%blocked%login%'
                              OR LOWER(action) LIKE '%login%failed%')""")
        failed_logins = cur.fetchone()[0] or 0
    else:
        cur.execute("SELECT COUNT(*) FROM audit_logs WHERE institute_id=? AND datetime(created_at) >= datetime('now', '-24 hours')", (institute_id,))
        last_24h = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM audit_logs WHERE institute_id=? AND datetime(created_at) >= datetime('now', '-7 days')", (institute_id,))
        last_7d = cur.fetchone()[0] or 0
        cur.execute("""SELECT COUNT(*) FROM audit_logs
                       WHERE institute_id=?
                       AND (LOWER(action) LIKE '%failed%login%'
                            OR LOWER(action) LIKE '%blocked%login%'
                            OR LOWER(action) LIKE '%login%failed%')""", (institute_id,))
        failed_logins = cur.fetchone()[0] or 0
    conn.close()
    return {
        "total": total,
        "today": today,
        "actors": actors,
        "unique_actors": actors,
        "last_24h": last_24h,
        "last_7d": last_7d,
        "failed_logins": failed_logins
    }


_ensure_compatibility_schema()
