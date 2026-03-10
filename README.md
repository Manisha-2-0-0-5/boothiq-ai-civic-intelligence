# 🗳️ BoothIQ – AI Civic Intelligence Platform v2.0

Full-stack AI-powered booth management system.
**Python + FastAPI + Streamlit · Email + SMS Notifications**

---

## 📁 Project Structure

```
boothiq/
├── app.py                        ← Streamlit frontend (7 pages)
├── requirements.txt
├── README.md
└── backend/
    ├── main.py                   ← FastAPI REST API
    ├── data_store.py             ← Sample voter + feedback data
    ├── voter_segmentation.py     ← K-Means AI clustering
    ├── scheme_recommendation.py  ← Rule-based scheme engine (15 schemes)
    ├── sentiment_analysis.py     ← NLP keyword sentiment scorer
    └── notifier.py               ← Email (Gmail) + SMS (Twilio) engine
```

---

## 🚀 Setup & Run

### Step 1 – Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 – Set credentials (for Email/SMS)
```bash
# Windows
set BOOTHIQ_EMAIL=your_gmail@gmail.com
set BOOTHIQ_EMAIL_PWD=xxxx xxxx xxxx xxxx
set TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
set TWILIO_AUTH_TOKEN=your_auth_token
set TWILIO_FROM_NUMBER=+1XXXXXXXXXX
```

### Step 3 – Run
```bash
# Streamlit Dashboard
py -m streamlit run app.py         →  http://localhost:8501

# FastAPI Backend (optional)
cd backend
py -m uvicorn main:app --reload    →  http://localhost:8000/docs
```

---

## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| 📊 Dashboard | KPI cards + 4 live Plotly charts |
| 👥 Voter Segments | K-Means AI clusters + age/scheme charts + voter table |
| 📋 Scheme Recommender | Live profile form → 15-scheme matching + coverage gap |
| 💬 Sentiment Analysis | Live NLP analyzer + issue heatmap + feedback log |
| 🔍 Voter Lookup | Full profile + scheme enrollment status |
| ➕ Add Voter | Register new voter + live eligibility preview |
| 🔔 Send Notification | Filter → Email/SMS → log with delivery stats |

---

## 🔔 Notification Filters

| Filter | Targets |
|--------|---------|
| 🏘️ Booth | All voters in a booth or all booths |
| 👤 Occupation | Farmers, Students, Teachers, etc. |
| 🔢 Age Group | Youth / Young Adult / Middle Aged / Senior |
| ♀️ Gender | Male / Female / Other |
| ✋ Individual | Handpick specific voters by name/ID |

---

## 🔗 API Endpoints

```
GET  /dashboard/stats
GET  /voters
GET  /voters/booth/{booth_id}
POST /voters
GET  /segmentation/{booth_id}
POST /schemes/recommend
GET  /schemes/voter/{voter_id}
GET  /schemes/coverage/{booth_id}
POST /sentiment/analyze
GET  /sentiment/{booth_id}
POST /notify
```

---

## 📧 Gmail App Password Setup

1. Enable 2-Factor Auth on Gmail
2. Go to: https://myaccount.google.com/apppasswords
3. Generate App Password → select "Mail"
4. Use that 16-char password (NOT your regular password)

## 📱 Twilio SMS Setup

1. Sign up free at https://www.twilio.com
2. Get Account SID + Auth Token from Console
3. Get a Twilio phone number
4. `pip install twilio`
