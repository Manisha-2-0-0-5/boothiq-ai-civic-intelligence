# backend/main.py  –  BoothIQ FastAPI REST API
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn, sys, os
sys.path.insert(0, os.path.dirname(__file__))

from data_store            import voters_db, feedback_db
from voter_segmentation    import segment_voters, get_booth_distribution
from scheme_recommendation import recommend_schemes, get_booth_scheme_coverage
from sentiment_analysis    import analyze_sentiment, get_booth_sentiment_summary
from notifier              import bulk_notify

app = FastAPI(title="BoothIQ API", version="2.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

class Voter(BaseModel):
    voter_id:str; name:str; age:int; gender:str; occupation:str; income:int
    booth_id:str; land_ownership:bool; schemes_enrolled:List[str]=[]
    email:str=""; phone:str=""

class FeedbackIn(BaseModel):
    booth_id:str; text:str; voter_id:Optional[str]=None

class SchemeReq(BaseModel):
    age:int; occupation:str; income:int; land_ownership:bool; gender:str

class NotifyReq(BaseModel):
    voter_ids:List[str]; title:str; body:str
    notif_type:str="📢 General Announcement"; priority:str="Normal"
    link:str=""; via_email:bool=True; via_sms:bool=False

@app.get("/")
def root(): return {"message":"BoothIQ API v2.0 Running"}

# ── Voters ────────────────────────────────────────────────────────────────────
@app.get("/voters")
def get_voters(): return voters_db

@app.get("/voters/{voter_id}")
def get_voter(voter_id:str):
    v = next((v for v in voters_db if v["voter_id"]==voter_id),None)
    if not v: raise HTTPException(404,"Voter not found")
    return v

@app.post("/voters")
def add_voter(v:Voter):
    if any(x["voter_id"]==v.voter_id for x in voters_db):
        raise HTTPException(400,"Voter ID already exists")
    voters_db.append(v.dict()); return {"message":"Added","voter_id":v.voter_id}

@app.get("/voters/booth/{booth_id}")
def booth_voters(booth_id:str):
    bv = [v for v in voters_db if v["booth_id"]==booth_id]
    if not bv: raise HTTPException(404,"No voters found")
    return {"booth_id":booth_id,"total":len(bv),"voters":bv}

# ── Segmentation ──────────────────────────────────────────────────────────────
@app.get("/segmentation/{booth_id}")
def segmentation(booth_id:str):
    bv = [v for v in voters_db if v["booth_id"]==booth_id]
    if not bv: raise HTTPException(404,"No voters")
    return {"booth_id":booth_id,"segments":segment_voters(bv),"distribution":get_booth_distribution(bv)}

# ── Schemes ───────────────────────────────────────────────────────────────────
@app.post("/schemes/recommend")
def schemes(r:SchemeReq):
    s = recommend_schemes(r.age,r.occupation,r.income,r.land_ownership,r.gender)
    return {"schemes":s,"total":len(s)}

@app.get("/schemes/voter/{voter_id}")
def voter_schemes(voter_id:str):
    v = next((v for v in voters_db if v["voter_id"]==voter_id),None)
    if not v: raise HTTPException(404,"Voter not found")
    return {"schemes":recommend_schemes(v["age"],v["occupation"],v["income"],v["land_ownership"],v["gender"]),
            "enrolled":v["schemes_enrolled"]}

@app.get("/schemes/coverage/{booth_id}")
def coverage(booth_id:str):
    bv = [v for v in voters_db if v["booth_id"]==booth_id]
    if not bv: raise HTTPException(404,"No voters")
    return get_booth_scheme_coverage(bv)

# ── Sentiment ─────────────────────────────────────────────────────────────────
@app.post("/sentiment/analyze")
def sentiment(fb:FeedbackIn):
    r = analyze_sentiment(fb.text)
    entry = {"booth_id":fb.booth_id,"voter_id":fb.voter_id,"text":fb.text,
             "sentiment":r["sentiment"],"score":r["score"],"issues":r["issues"]}
    feedback_db.append(entry); return entry

@app.get("/sentiment/{booth_id}")
def booth_sentiment(booth_id:str):
    bf = [f for f in feedback_db if f["booth_id"]==booth_id]
    if not bf: raise HTTPException(404,"No feedback")
    return get_booth_sentiment_summary(bf)

# ── Notifications ─────────────────────────────────────────────────────────────
@app.post("/notify")
def notify(req:NotifyReq):
    targets = [v for v in voters_db if v["voter_id"] in req.voter_ids]
    if not targets: raise HTTPException(404,"No matching voters")
    result = bulk_notify(targets,req.title,req.body,req.notif_type,req.priority,
                         req.link,req.via_email,req.via_sms)
    return result

# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.get("/dashboard/stats")
def stats():
    from collections import Counter
    return {
        "total_voters":    len(voters_db),
        "total_booths":    len(set(v["booth_id"] for v in voters_db)),
        "total_feedback":  len(feedback_db),
        "sentiment":       dict(Counter(f.get("sentiment","Neutral") for f in feedback_db)),
        "occupations":     dict(Counter(v["occupation"] for v in voters_db)),
        "gender":          dict(Counter(v["gender"]     for v in voters_db)),
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
