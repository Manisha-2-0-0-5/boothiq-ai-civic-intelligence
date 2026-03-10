# backend/data_store.py  –  BoothIQ in-memory data store

voters_db = [
    # ── Booth B01 ──────────────────────────────────────────────────────────────
    {"voter_id":"V001","name":"Ramesh Kumar",  "age":45,"gender":"Male",  "occupation":"Farmer",   "income":80000, "booth_id":"B01","land_ownership":True, "schemes_enrolled":["PM-KISAN"],                       "email":"ramesh.kumar@example.com",  "phone":"+911234567801"},
    {"voter_id":"V002","name":"Sunita Devi",   "age":32,"gender":"Female","occupation":"Homemaker","income":0,     "booth_id":"B01","land_ownership":False,"schemes_enrolled":[],                                  "email":"sunita.devi@example.com",   "phone":"+911234567802"},
    {"voter_id":"V003","name":"Arjun Sharma",  "age":21,"gender":"Male",  "occupation":"Student",  "income":0,     "booth_id":"B01","land_ownership":False,"schemes_enrolled":[],                                  "email":"arjun.sharma@example.com",  "phone":"+911234567803"},
    {"voter_id":"V004","name":"Meena Patel",   "age":55,"gender":"Female","occupation":"Farmer",   "income":95000, "booth_id":"B01","land_ownership":True, "schemes_enrolled":["PM-KISAN","Fasal Bima"],           "email":"meena.patel@example.com",   "phone":"+911234567804"},
    {"voter_id":"V005","name":"Suresh Yadav",  "age":67,"gender":"Male",  "occupation":"Retired",  "income":12000, "booth_id":"B01","land_ownership":False,"schemes_enrolled":["Old Age Pension"],                 "email":"suresh.yadav@example.com",  "phone":"+911234567805"},
    # ── Booth B02 ──────────────────────────────────────────────────────────────
    {"voter_id":"V006","name":"Priya Singh",   "age":28,"gender":"Female","occupation":"Teacher",  "income":350000,"booth_id":"B02","land_ownership":False,"schemes_enrolled":[],                                  "email":"priya.singh@example.com",   "phone":"+911234567806"},
    {"voter_id":"V007","name":"Mohan Lal",     "age":40,"gender":"Male",  "occupation":"Business", "income":700000,"booth_id":"B02","land_ownership":True, "schemes_enrolled":[],                                  "email":"mohan.lal@example.com",     "phone":"+911234567807"},
    {"voter_id":"V008","name":"Kavita Verma",  "age":35,"gender":"Female","occupation":"Homemaker","income":0,     "booth_id":"B02","land_ownership":False,"schemes_enrolled":["Ujjwala Yojana"],                   "email":"kavita.verma@example.com",  "phone":"+911234567808"},
    {"voter_id":"V009","name":"Deepak Mishra", "age":23,"gender":"Male",  "occupation":"Student",  "income":0,     "booth_id":"B02","land_ownership":False,"schemes_enrolled":["NSP Scholarship"],                 "email":"deepak.mishra@example.com", "phone":"+911234567809"},
    {"voter_id":"V010","name":"Lata Gupta",    "age":70,"gender":"Female","occupation":"Retired",  "income":8000,  "booth_id":"B02","land_ownership":False,"schemes_enrolled":["Old Age Pension","Ayushman Bharat"],"email":"lata.gupta@example.com",    "phone":"+911234567810"},
    # ── Booth B03 ──────────────────────────────────────────────────────────────
    {"voter_id":"V011","name":"Vikram Rawat",  "age":38,"gender":"Male",  "occupation":"Farmer",   "income":60000, "booth_id":"B03","land_ownership":True, "schemes_enrolled":["PM-KISAN"],                        "email":"vikram.rawat@example.com",  "phone":"+911234567811"},
    {"voter_id":"V012","name":"Anjali Tiwari", "age":26,"gender":"Female","occupation":"Teacher",  "income":280000,"booth_id":"B03","land_ownership":False,"schemes_enrolled":[],                                  "email":"anjali.tiwari@example.com", "phone":"+911234567812"},
    {"voter_id":"V013","name":"Ravi Shankar",  "age":50,"gender":"Male",  "occupation":"Business", "income":500000,"booth_id":"B03","land_ownership":True, "schemes_enrolled":[],                                  "email":"ravi.shankar@example.com",  "phone":"+911234567813"},
    {"voter_id":"V014","name":"Geeta Rani",    "age":43,"gender":"Female","occupation":"Farmer",   "income":72000, "booth_id":"B03","land_ownership":True, "schemes_enrolled":["PM-KISAN"],                        "email":"geeta.rani@example.com",    "phone":"+911234567814"},
    {"voter_id":"V015","name":"Ashok Pandey",  "age":19,"gender":"Male",  "occupation":"Student",  "income":0,     "booth_id":"B03","land_ownership":False,"schemes_enrolled":[],                                  "email":"ashok.pandey@example.com",  "phone":"+911234567815"},
]

feedback_db = [
    {"booth_id":"B01","voter_id":"V001","text":"Roads are very bad in our area, no repair done in years.",        "sentiment":"Negative","score":-0.7,"issues":["road","infrastructure"]},
    {"booth_id":"B01","voter_id":"V002","text":"Water supply has improved a lot recently, very happy.",           "sentiment":"Positive","score": 0.8,"issues":["water"]},
    {"booth_id":"B01","voter_id":"V003","text":"Electricity cuts are very frequent, it is a big problem.",       "sentiment":"Negative","score":-0.6,"issues":["electricity"]},
    {"booth_id":"B02","voter_id":"V006","text":"New school building construction is great for our children.",    "sentiment":"Positive","score": 0.9,"issues":["education"]},
    {"booth_id":"B02","voter_id":"V007","text":"Drainage system is broken, flooding every monsoon season.",      "sentiment":"Negative","score":-0.8,"issues":["drainage","flooding"]},
    {"booth_id":"B02","voter_id":"V008","text":"Health camp was helpful but needs to happen more often.",        "sentiment":"Neutral", "score": 0.1,"issues":["health"]},
    {"booth_id":"B03","voter_id":"V011","text":"Crop insurance process is too slow and very complicated.",       "sentiment":"Negative","score":-0.5,"issues":["agriculture","insurance"]},
    {"booth_id":"B03","voter_id":"V012","text":"Street lights installed last month, night safety improved.",     "sentiment":"Positive","score": 0.75,"issues":["street light","safety"]},
    {"booth_id":"B03","voter_id":"V013","text":"Everything is fine in our area, no major complaints at all.",   "sentiment":"Positive","score": 0.6,"issues":[]},
]
