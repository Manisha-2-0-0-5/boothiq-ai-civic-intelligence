# backend/sentiment_analysis.py  –  NLP keyword sentiment engine
from collections import Counter

POS = {"good":0.6,"great":0.8,"excellent":0.9,"improved":0.7,"better":0.6,"happy":0.8,
       "satisfied":0.7,"helpful":0.7,"clean":0.6,"completed":0.6,"fixed":0.7,
       "working":0.5,"progress":0.6,"installed":0.6,"received":0.5,"available":0.4,
       "thanks":0.5,"appreciate":0.6,"best":0.8,"safe":0.6,"resolved":0.7,
       "new":0.4,"built":0.5,"construction":0.4,"fast":0.5}

NEG = {"bad":-0.6,"poor":-0.6,"terrible":-0.9,"broken":-0.8,"problem":-0.6,
       "issue":-0.5,"complaint":-0.6,"dirty":-0.7,"slow":-0.5,"never":-0.7,
       "worst":-0.9,"failure":-0.8,"flood":-0.7,"flooding":-0.8,
       "complicated":-0.5,"corrupt":-0.9,"delayed":-0.6,"damaged":-0.7,
       "incomplete":-0.6,"waste":-0.7,"ignored":-0.7,"repair":-0.4,
       "cuts":-0.5,"cut":-0.4,"frequent":-0.3,"no":-0.3,"not":-0.3}

ISSUE_KW = {
    "road":        ["road","roads","street","pothole","repair","pavement"],
    "water":       ["water","supply","pipeline","tap","borewell"],
    "electricity": ["electricity","power","light","voltage","current","cuts"],
    "health":      ["health","hospital","doctor","medicine","clinic","medical"],
    "education":   ["school","college","teacher","education","study","building"],
    "agriculture": ["crop","farm","farmer","seed","fertilizer","harvest","kisan"],
    "insurance":   ["insurance","claim","policy","compensation"],
    "drainage":    ["drain","drainage","sewer","overflow","flood","flooding"],
    "safety":      ["safety","security","crime","police","street light"],
    "housing":     ["house","housing","shelter","home"],
    "sanitation":  ["toilet","sanitation","garbage","waste","hygiene"],
}

def analyze_sentiment(text):
    words = text.lower().split()
    score = sum(POS.get(w,0)+NEG.get(w,0) for w in words)
    score = max(-1.0, min(1.0, round(score,2)))
    sentiment = "Positive" if score>=0.3 else ("Negative" if score<=-0.2 else "Neutral")
    tl = text.lower()
    issues = [iss for iss,kws in ISSUE_KW.items() if any(k in tl for k in kws)]
    return {"sentiment":sentiment,"score":score,"issues":issues}

def get_booth_sentiment_summary(fb_list):
    if not fb_list: return {}
    total = len(fb_list)
    sc    = Counter(f["sentiment"] for f in fb_list)
    pos,neg,neu = sc.get("Positive",0),sc.get("Negative",0),sc.get("Neutral",0)
    overall = "Positive" if pos>neg and pos>neu else ("Negative" if neg>pos and neg>neu else "Neutral")
    all_issues = []
    for f in fb_list: all_issues.extend(f.get("issues",[]))
    freq = dict(Counter(all_issues))
    severity = {iss: ("High" if cnt/total*100>=60 else ("Medium" if cnt/total*100>=30 else "Low"))
                for iss,cnt in freq.items()}
    return {
        "overall_sentiment": overall,
        "average_score":     round(sum(f.get("score",0) for f in fb_list)/total,2),
        "breakdown": {
            "Positive":pos,"Negative":neg,"Neutral":neu,
            "positive_percent":round(pos/total*100,1),
            "negative_percent":round(neg/total*100,1),
            "neutral_percent": round(neu/total*100,1),
        },
        "issue_heatmap":  freq,
        "issue_severity": severity,
        "top_issue": max(freq,key=freq.get) if freq else None,
    }
