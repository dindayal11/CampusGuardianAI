# =========================================================
# CAMPUS LOCATION CONFIGURATION
# =========================================================
#
# This file contains the default campus map configuration.
#
# IMPORTANT:
# Future versions will load these values from the database
# for each institute.
# =========================================================


# =========================================================
# DEFAULT CAMPUS CENTER
# =========================================================

CAMPUS_CENTER = {
    "latitude": 30.37869,
    "longitude": 77.82510
}


# =========================================================
# DEFAULT CAMPUS LOCATIONS
# =========================================================

CAMPUS_LOCATIONS = {

    "Main Gate": {
        "latitude": 30.37869,
        "longitude": 77.82510
    },

    "Academic Block": {
        "latitude": 30.37895,
        "longitude": 77.82530
    },

    "CSE Department": {
        "latitude": 30.37905,
        "longitude": 77.82545
    },

    "Library": {
        "latitude": 30.37885,
        "longitude": 77.82555
    },

    "Canteen": {
        "latitude": 30.37860,
        "longitude": 77.82550
    },

    "Parking Area": {
        "latitude": 30.37845,
        "longitude": 77.82495
    },

    "Hostel Block A": {
        "latitude": 30.37920,
        "longitude": 77.82580
    },

    "Playground": {
        "latitude": 30.37830,
        "longitude": 77.82580
    }
}


# =========================================================
# GET CAMPUS CONFIGURATION
# =========================================================

def get_campus_config(institute_id=None):

    """
    Returns campus configuration.

    Currently the project uses the default configuration.
    Database-based institute customization will be connected
    in the next step.
    """

    return {
        "center": CAMPUS_CENTER,
        "locations": CAMPUS_LOCATIONS
    }


# =========================================================
# GET CAMPUS CENTER
# =========================================================

def get_campus_center(institute_id=None):

    config = get_campus_config(
        institute_id
    )

    return config["center"]


# =========================================================
# GET CAMPUS LOCATIONS
# =========================================================

def get_campus_locations(institute_id=None):

    config = get_campus_config(
        institute_id
    )

    return config["locations"]