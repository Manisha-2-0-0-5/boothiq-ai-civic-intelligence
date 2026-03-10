# backend/voter_segmentation.py  –  K-Means AI segmentation
import numpy as np
from collections import Counter

OCCUPATION_SEGMENT_MAP = {
    "Farmer":"Farmers","Student":"Youth Voters","Teacher":"Working Class",
    "Business":"Business Owners","Homemaker":"Women / Homemakers",
    "Retired":"Senior Citizens","Labour":"Working Class","Govt":"Working Class",
}

def get_age_group(age):
    if age < 25:    return "Youth (18-24)"
    elif age < 40:  return "Young Adult (25-39)"
    elif age < 60:  return "Middle Aged (40-59)"
    else:           return "Senior (60+)"

def get_income_group(income):
    if income == 0:       return "No Income"
    elif income < 100000: return "Low Income"
    elif income < 500000: return "Middle Income"
    else:                 return "High Income"

def _kmeans(data, k=4, iters=100):
    arr = np.array(data, dtype=float)
    if len(arr) < k: return list(range(len(arr)))
    mx = arr.max(axis=0); mx[mx==0] = 1
    norm = arr / mx
    np.random.seed(42)
    centroids = norm[np.random.choice(len(norm), k, replace=False)].copy()
    labels = np.zeros(len(norm), dtype=int)
    for _ in range(iters):
        for i,pt in enumerate(norm):
            labels[i] = int(np.argmin([np.linalg.norm(pt-c) for c in centroids]))
        for j in range(k):
            pts = norm[labels==j]
            if len(pts): centroids[j] = pts.mean(axis=0)
    return labels.tolist()

def segment_voters(voters):
    if not voters: return {}
    labels = _kmeans([[v["age"],v["income"]] for v in voters], k=min(4,len(voters)))
    clusters = {}
    for i,v in enumerate(voters): clusters.setdefault(labels[i],[]).append(v)
    result = {}
    for cid,cvs in clusters.items():
        occ   = Counter(v["occupation"] for v in cvs).most_common(1)[0][0]
        avg_a = round(sum(v["age"]    for v in cvs)/len(cvs),1)
        avg_i = round(sum(v["income"] for v in cvs)/len(cvs),0)
        result[f"Segment_{cid+1}"] = {
            "label":               OCCUPATION_SEGMENT_MAP.get(occ,"General"),
            "count":               len(cvs),
            "avg_age":             avg_a,
            "avg_income":          avg_i,
            "dominant_occupation": occ,
            "age_group":           get_age_group(int(avg_a)),
            "income_group":        get_income_group(int(avg_i)),
            "voters":              [v["voter_id"] for v in cvs],
        }
    return result

def get_booth_distribution(voters):
    if not voters: return {}
    total    = len(voters)
    enrolled = sum(1 for v in voters if v["schemes_enrolled"])
    return {
        "total":         total,
        "age_groups":    dict(Counter(get_age_group(v["age"])      for v in voters)),
        "gender":        dict(Counter(v["gender"]                   for v in voters)),
        "occupations":   dict(Counter(v["occupation"]               for v in voters)),
        "income_groups": dict(Counter(get_income_group(v["income"]) for v in voters)),
        "scheme_coverage": {
            "enrolled":         enrolled,
            "not_enrolled":     total - enrolled,
            "coverage_percent": round(enrolled/total*100,1),
        },
    }
