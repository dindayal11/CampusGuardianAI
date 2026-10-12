
# =========================================================
# CAMPUS GUARDIAN AI
# COMPLAINT ANALYZER
# =========================================================


def analyze_complaint(title, description):

    text = (title + " " + description).lower()


    # =====================================================
    # CATEGORY KEYWORDS
    # =====================================================

    categories = {

        # -------------------------------------------------
        # ELECTRICAL
        # -------------------------------------------------

        "Electrical": [

            # English
            "electric",
            "electricity",
            "electrical",
            "wire",
            "wiring",
            "cable",
            "socket",
            "switch",
            "plug",
            "power",
            "current",
            "voltage",
            "fuse",
            "mcb",
            "spark",
            "sparks",
            "sparking",
            "short circuit",
            "shock",
            "electric shock",
            "bulb",
            "light",
            "tube light",
            "led",
            "fan",
            "ceiling fan",
            "exhaust fan",
            "ac",
            "air conditioner",
            "cooler",
            "charging point",
            "charger",
            "power cut",
            "power failure",
            "no power",
            "light not working",
            "fan not working",
            "switch not working",
            "socket not working",
            "burning smell",
            "electrical fault",
            "electrical problem",
            "wiring problem",
            "power problem",

            # Hinglish / Hindi
            "bijli",
            "bijli nahi",
            "bijli nhi",
            "light nahi",
            "light nhi",
            "pankha",
            "pankha nahi",
            "pankha nhi",
            "bulb kharab",
            "fan kharab",
            "switch kharab",
            "socket kharab",
            "current lag",
            "karent",
            "bijli ki problem",
            "bijli ki dikkat",
            "electric ki problem"
        ],


        # -------------------------------------------------
        # WATER
        # -------------------------------------------------

        "Water": [

            # English
            "water",
            "water supply",
            "water shortage",
            "no water",
            "less water",
            "dirty water",
            "leak",
            "leakage",
            "leaking",
            "pipe",
            "pipeline",
            "tap",
            "faucet",
            "shower",
            "toilet water",
            "bathroom water",
            "flush",
            "tank",
            "water tank",
            "overhead tank",
            "drainage",
            "drain",
            "overflow",
            "sewage",
            "sewer",
            "seepage",
            "waterlogging",
            "flooding",
            "wet floor",
            "water pressure",
            "low water pressure",
            "water problem",
            "tap broken",
            "pipe broken",
            "pipe burst",
            "water not coming",

            # Hinglish / Hindi
            "pani",
            "paani",
            "pani nahi",
            "paani nahi",
            "pani nhi",
            "paani nhi",
            "nal",
            "nal ka pani",
            "nal kharab",
            "tank khali",
            "pani leak",
            "paani leak",
            "pani bhar",
            "pani jama",
            "ganda pani",
            "ganda paani",
            "pani ki dikkat",
            "paani ki dikkat",
            "pani ki problem",
            "paani ki problem",
            "flush kharab",
            "nal se pani nahi"
        ],


        # -------------------------------------------------
        # INFRASTRUCTURE
        # -------------------------------------------------

        "Infrastructure": [

            # English
            "broken",
            "break",
            "damage",
            "damaged",
            "building",
            "wall",
            "walls",
            "floor",
            "ceiling",
            "roof",
            "door",
            "window",
            "gate",
            "stairs",
            "staircase",
            "lift",
            "elevator",
            "corridor",
            "classroom",
            "laboratory",
            "lab",
            "hostel room",
            "room",
            "furniture",
            "chair",
            "chairs",
            "table",
            "desk",
            "bench",
            "board",
            "blackboard",
            "whiteboard",
            "locker",
            "bed",
            "mattress",
            "plaster",
            "crack",
            "cracked",
            "pavement",
            "pathway",
            "road",
            "parking area",
            "roof damage",
            "wall damage",
            "door broken",
            "window broken",
            "floor damaged",
            "infrastructure problem",
            "building damage",
            "furniture broken",

            # Hinglish / Hindi
            "toota",
            "tuta",
            "tuti",
            "tooti",
            "kharab",
            "damage hai",
            "deewar",
            "chhat",
            "darwaza",
            "khidki",
            "seedhi",
            "sidi",
            "kamra",
            "kursi",
            "mez",
            "table kharab",
            "bench kharab",
            "farsh",
            "building kharab",
            "deewar me crack",
            "samaan kharab"
        ],


        # -------------------------------------------------
        # SAFETY
        # -------------------------------------------------

        "Safety": [

            # English
            "unsafe",
            "danger",
            "dangerous",
            "security",
            "threat",
            "threatening",
            "suspicious",
            "suspicious person",
            "suspicious activity",
            "fight",
            "fighting",
            "violence",
            "attack",
            "weapon",
            "theft",
            "stealing",
            "stolen",
            "robbery",
            "burglary",
            "intruder",
            "trespassing",
            "unauthorized entry",
            "cctv",
            "camera",
            "security camera",
            "security guard",
            "guard",
            "dark",
            "darkness",
            "dark area",
            "street light",
            "streetlight",
            "no security",
            "security problem",
            "emergency",
            "accident",
            "fire",
            "smoke",
            "fire alarm",
            "unsafe area",
            "unsafe place",
            "emergency exit",
            "exit blocked",
            "blocked exit",

            # Hinglish / Hindi
            "suraksha",
            "surakshit nahi",
            "khatra",
            "danger hai",
            "dhamki",
            "dhamki dena",
            "maar peet",
            "ladai",
            "jhagda",
            "chori",
            "chor",
            "chori ho gayi",
            "andhera",
            "andhera hai",
            "cctv nahi",
            "guard nahi",
            "security nahi",
            "security ki problem",
            "security ki dikkat"
        ],


        # -------------------------------------------------
        # HARASSMENT
        # -------------------------------------------------

        "Harassment": [

            # English
            "harassment",
            "harass",
            "harassed",
            "abuse",
            "abusive",
            "abusing",
            "misbehave",
            "misbehavior",
            "molest",
            "molestation",
            "sexual harassment",
            "inappropriate",
            "inappropriate behaviour",
            "inappropriate behavior",
            "verbal abuse",
            "mental harassment",
            "threatening",
            "stalking",
            "bullying",
            "teasing",
            "blackmail",
            "intimidation",
            "humiliate",
            "humiliation",
            "unwanted contact",
            "unwanted message",
            "unwanted behaviour",
            "unwanted behavior",

            # Hinglish / Hindi
            "pareshan",
            "pareshan karna",
            "pareshan karta",
            "pareshan karti",
            "tang karna",
            "tang karta",
            "tang karti",
            "bad behavior",
            "bad behaviour",
            "badtameezi",
            "galat behaviour",
            "galat behavior",
            "galat bartav",
            "dhamki deta",
            "dhamki deti",
            "gali",
            "gaali",
            "gali dena",
            "gaali dena",
            "apmaan",
            "beizzati",
            "blackmail karna",
            "peecha karna",
            "ghoorna"
        ],


        # -------------------------------------------------
        # RAGGING
        # -------------------------------------------------

        "Ragging": [

            # English
            "ragging",
            "ragged",
            "rag",
            "senior bullying",
            "senior bully",
            "junior bullying",
            "forced by senior",
            "forced introduction",
            "forced activity",
            "senior forced",
            "senior threatening",
            "senior harassment",
            "junior harassment",
            "freshers",
            "fresher",
            "humiliation by senior",
            "senior abuse",
            "senior misbehavior",
            "senior misconduct",

            # Hinglish / Hindi
            "senior pareshan",
            "senior tang",
            "senior dhamki",
            "senior ne mara",
            "senior maar",
            "senior force",
            "senior zabardasti",
            "zabardasti introduction",
            "zabardasti kaam",
            "junior ko pareshan",
            "junior ko tang",
            "ragging kar raha",
            "ragging kar rahe",
            "senior bully",
            "senior bullying"
        ],


        # -------------------------------------------------
        # CLEANLINESS
        # -------------------------------------------------

        "Cleanliness": [

            # English
            "dirty",
            "dirt",
            "garbage",
            "waste",
            "trash",
            "rubbish",
            "dustbin",
            "dust",
            "dusty",
            "cleanliness",
            "cleaning",
            "unclean",
            "filthy",
            "bad smell",
            "smell",
            "stink",
            "stinking",
            "toilet dirty",
            "washroom dirty",
            "bathroom dirty",
            "dirty floor",
            "dirty room",
            "dirty water",
            "mosquito",
            "mosquitoes",
            "insects",
            "flies",
            "cockroach",
            "rats",
            "rat",
            "pest",
            "pests",
            "sanitation",
            "hygiene",
            "food hygiene",
            "overflowing dustbin",
            "garbage collection",
            "waste collection",

            # Hinglish / Hindi
            "gandagi",
            "ganda",
            "gandi",
            "kachra",
            "kuuda",
            "kooda",
            "dustbin nahi",
            "safai",
            "safai nahi",
            "safai nhi",
            "badbu",
            "badhbu",
            "machhar",
            "keede",
            "makkhi",
            "cockroach hai",
            "chhipkali",
            "toilet ganda",
            "washroom ganda",
            "bathroom ganda",
            "kamra ganda"
        ],


        # -------------------------------------------------
        # MEDICAL EMERGENCY
        # -------------------------------------------------

        "Medical Emergency": [

            # English
            "medical",
            "medical emergency",
            "emergency",
            "injury",
            "injured",
            "blood",
            "bleeding",
            "accident",
            "unconscious",
            "fainted",
            "fainting",
            "heart attack",
            "chest pain",
            "breathing problem",
            "difficulty breathing",
            "breathless",
            "severe pain",
            "pain",
            "fever",
            "sick",
            "illness",
            "disease",
            "vomiting",
            "vomit",
            "dizziness",
            "headache",
            "fracture",
            "burn",
            "burned",
            "wound",
            "ambulance",
            "first aid",
            "doctor",
            "hospital",
            "medicine",
            "seizure",
            "fits",
            "poisoning",
            "food poisoning",
            "snake bite",
            "dog bite",

            # Hinglish / Hindi
            "tabiyat kharab",
            "tabiyat kharab hai",
            "bimaar",
            "bimari",
            "bukhar",
            "chot",
            "chot lag",
            "khoon",
            "khoon nikal",
            "behosh",
            "behoshi",
            "chakkar",
            "saans nahi",
            "saans lene me dikkat",
            "seene me dard",
            "pet dard",
            "sir dard",
            "dawai",
            "doctor chahiye",
            "ambulance chahiye",
            "hospital chahiye",
            "jal gaya",
            "jalne ki chot",
            "haddi toot",
            "khana kharab",
            "food poisoning"
        ]
    }


    # =====================================================
    # DETECT CATEGORY
    # =====================================================

    detected_category = "Other"

    max_matches = 0


    for category, keywords in categories.items():

        matches = 0

        for keyword in keywords:

            if keyword in text:

                matches += 1


        if matches > max_matches:

            max_matches = matches

            detected_category = category


    # =====================================================
    # PRIORITY DETECTION
    # =====================================================

    # -----------------------------------------------------
    # CRITICAL
    # -----------------------------------------------------

    critical_keywords = [

        # Major emergencies
        "fire",
        "fire accident",
        "fire emergency",
        "explosion",
        "blast",
        "gas leak",
        "gas leakage",

        # Electrical danger
        "electric shock",
        "electrical shock",
        "live wire",
        "exposed wire",
        "high voltage",
        "short circuit",
        "sparking",
        "sparks",

        # Medical emergency
        "unconscious",
        "unconscious person",
        "not breathing",
        "cannot breathe",
        "difficulty breathing",
        "breathing problem",
        "heart attack",
        "cardiac arrest",
        "severe bleeding",
        "heavy bleeding",
        "blood loss",
        "major accident",
        "serious injury",
        "severe injury",
        "critical injury",
        "ambulance",
        "life danger",
        "life threatening",

        # Safety
        "weapon",
        "gun",
        "knife attack",
        "violent attack",
        "armed",
        "serious threat",
        "immediate danger",

        # Other emergencies
        "emergency",
        "urgent emergency"
    ]


    # -----------------------------------------------------
    # HIGH
    # -----------------------------------------------------

    high_keywords = [

        # Safety
        "danger",
        "dangerous",
        "unsafe",
        "threat",
        "threatening",
        "suspicious",
        "fight",
        "fighting",
        "violence",
        "attack",
        "theft",
        "robbery",
        "burglary",
        "intruder",
        "trespassing",

        # Electrical
        "broken wire",
        "exposed cable",
        "electrical fault",
        "electrical problem",
        "burning smell",

        # Harassment / Ragging
        "harassment",
        "harassed",
        "sexual harassment",
        "molest",
        "molestation",
        "stalking",
        "blackmail",
        "intimidation",
        "ragging",
        "senior bullying",
        "senior threatening",
        "senior harassment",
        "forced by senior",

        # Medical
        "injury",
        "injured",
        "accident",
        "bleeding",
        "blood",
        "fracture",
        "burn",
        "fainted",
        "fainting",
        "severe pain",
        "chest pain",
        "fever",

        # Infrastructure
        "ceiling falling",
        "wall falling",
        "roof damage",
        "major damage",
        "broken staircase",
        "broken stairs",
        "broken railing",

        # Water
        "pipe burst",
        "major leakage",
        "heavy leakage",
        "water flooding",
        "flooding"
    ]


    # -----------------------------------------------------
    # MEDIUM
    # -----------------------------------------------------

    medium_keywords = [

        # General
        "not working",
        "not working properly",
        "problem",
        "issue",
        "complaint",
        "difficult",
        "difficulty",

        # Electrical
        "light not working",
        "fan not working",
        "switch not working",
        "socket not working",
        "power cut",
        "power failure",
        "voltage problem",

        # Water
        "leak",
        "leakage",
        "water leakage",
        "water problem",
        "water shortage",
        "low water pressure",
        "drainage problem",
        "overflow",

        # Infrastructure
        "broken",
        "damage",
        "damaged",
        "crack",
        "cracked",
        "door broken",
        "window broken",
        "furniture broken",

        # Cleanliness
        "dirty",
        "garbage",
        "waste",
        "bad smell",
        "unclean",
        "mosquito",
        "cockroach",
        "pest",

        # Medical
        "pain",
        "headache",
        "vomiting",
        "dizziness",
        "sick",
        "illness",

        # Hindi / Hinglish
        "kharab",
        "dikkat",
        "problem hai",
        "pani nahi",
        "bijli nahi",
        "safai nahi",
        "ganda",
        "toota",
        "tuta"
    ]


    priority = "Low"


    # Critical has highest priority
    if any(keyword in text for keyword in critical_keywords):

        priority = "Critical"


    # High comes after Critical
    elif any(keyword in text for keyword in high_keywords):

        priority = "High"


    # Medium comes after High
    elif any(keyword in text for keyword in medium_keywords):

        priority = "Medium"


    # =====================================================
    # DEPARTMENT ASSIGNMENT
    # =====================================================

    departments = {

        "Electrical":
        "Electrical Maintenance Department",

        "Water":
        "Plumbing and Maintenance Department",

        "Infrastructure":
        "Infrastructure Maintenance Department",

        "Safety":
        "Campus Security Department",

        "Harassment":
        "Student Welfare and Security Department",

        "Ragging":
        "Anti-Ragging Committee",

        "Cleanliness":
        "Housekeeping Department",

        "Medical Emergency":
        "Campus Medical Emergency Team",

        "Other":
        "Campus Administration"
    }


    department = departments[detected_category]


    # =====================================================
    # RISK SCORE
    # =====================================================

    risk_scores = {

        "Low": 25,

        "Medium": 50,

        "High": 75,

        "Critical": 95
    }


    risk_score = risk_scores[priority]


    # =====================================================
    # RECOMMENDED ACTION
    # =====================================================

    actions = {

        "Low":
        "Monitor the issue and schedule maintenance if required.",

        "Medium":
        "Assign the responsible department and resolve the issue soon.",

        "High":
        "Immediate inspection is recommended. Take preventive safety measures.",

        "Critical":
        "Immediate action required. Secure the area and notify responsible authorities."
    }


    recommended_action = actions[priority]


    # =====================================================
    # FINAL RESULT
    # =====================================================

    return {

        "category": detected_category,

        "priority": priority,

        "department": department,

        "risk_score": risk_score,

        "recommended_action": recommended_action
    }

