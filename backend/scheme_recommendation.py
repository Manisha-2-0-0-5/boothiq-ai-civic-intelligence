# backend/scheme_recommendation.py  –  Rule-based AI scheme engine
SCHEMES = [
    {"name":"PM-KISAN",                    "desc":"₹6,000/year income support for farmers",              "cat":"Agriculture","fn": lambda a,o,i,l,g: o=="Farmer" and l and i<150000},
    {"name":"Pradhan Mantri Fasal Bima",   "desc":"Crop insurance scheme for farmers",                   "cat":"Agriculture","fn": lambda a,o,i,l,g: o=="Farmer" and l},
    {"name":"Kisan Credit Card",           "desc":"Short-term credit for farmers at low interest",        "cat":"Agriculture","fn": lambda a,o,i,l,g: o=="Farmer"},
    {"name":"National Scholarship Portal", "desc":"Merit and means-based scholarships for students",      "cat":"Education",  "fn": lambda a,o,i,l,g: o=="Student" and a<30 and i<250000},
    {"name":"PM Vidya Lakshmi",            "desc":"Education loan portal for higher studies",             "cat":"Education",  "fn": lambda a,o,i,l,g: o=="Student" and a<35},
    {"name":"Ayushman Bharat PMJAY",       "desc":"₹5 lakh/year health cover for poor families",         "cat":"Health",     "fn": lambda a,o,i,l,g: i<200000},
    {"name":"Janani Suraksha Yojana",      "desc":"Cash incentive for institutional deliveries",          "cat":"Health",     "fn": lambda a,o,i,l,g: g=="Female" and 18<=a<=45 and i<150000},
    {"name":"PM Ujjwala Yojana",           "desc":"Free LPG connection for women below poverty line",     "cat":"Welfare",    "fn": lambda a,o,i,l,g: g=="Female" and i<100000},
    {"name":"Beti Bachao Beti Padhao",     "desc":"Scheme for girl child welfare and education",          "cat":"Welfare",    "fn": lambda a,o,i,l,g: g=="Female" and a<25},
    {"name":"National Old Age Pension",    "desc":"Monthly pension for senior citizens below poverty",    "cat":"Pension",    "fn": lambda a,o,i,l,g: a>=60 and i<100000},
    {"name":"Atal Pension Yojana",         "desc":"Guaranteed pension for unorganized sector workers",    "cat":"Pension",    "fn": lambda a,o,i,l,g: 18<=a<=40 and o in ["Farmer","Labour","Homemaker"]},
    {"name":"PM MUDRA Yojana",             "desc":"Business loans up to ₹10 lakh for small enterprises", "cat":"Business",   "fn": lambda a,o,i,l,g: o=="Business" and i<1000000},
    {"name":"Stand Up India",              "desc":"Bank loans for SC/ST and women entrepreneurs",         "cat":"Business",   "fn": lambda a,o,i,l,g: g=="Female" and o=="Business"},
    {"name":"PM Awas Yojana Urban",        "desc":"Affordable housing for urban poor families",           "cat":"Housing",    "fn": lambda a,o,i,l,g: i<300000 and not l},
    {"name":"Sukanya Samriddhi Yojana",    "desc":"High-interest savings scheme for the girl child",      "cat":"Savings",    "fn": lambda a,o,i,l,g: g=="Female" and a<=10},
]

def recommend_schemes(age, occupation, income, land_ownership, gender):
    out = []
    for s in SCHEMES:
        try:
            if s["fn"](age, occupation, income, land_ownership, gender):
                out.append({"name":s["name"],"description":s["desc"],"category":s["cat"]})
        except Exception:
            pass
    return out

def get_booth_scheme_coverage(voters):
    total = len(voters)
    unenrolled = []
    for v in voters:
        rec     = {s["name"] for s in recommend_schemes(v["age"],v["occupation"],v["income"],v["land_ownership"],v["gender"])}
        missing = rec - set(v["schemes_enrolled"])
        if missing:
            unenrolled.append({"voter_id":v["voter_id"],"name":v["name"],"missing_schemes":list(missing)})
    return {
        "total_voters":           total,
        "voters_missing_schemes": len(unenrolled),
        "coverage_gap_percent":   round(len(unenrolled)/total*100,1) if total else 0,
        "details":                unenrolled,
    }
