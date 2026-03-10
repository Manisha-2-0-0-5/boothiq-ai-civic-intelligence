# app.py  –  BoothIQ Complete Streamlit Frontend  (all 7 pages)
from dotenv import load_dotenv
load_dotenv()
import streamlit as st

st.set_page_config(
    page_title="BoothIQ – AI Civic Intelligence",
    page_icon="🗳️", layout="wide",
    initial_sidebar_state="expanded",
)

import sys, os, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from data_store            import voters_db, feedback_db
from voter_segmentation    import segment_voters, get_booth_distribution
from scheme_recommendation import recommend_schemes, get_booth_scheme_coverage
from sentiment_analysis    import analyze_sentiment, get_booth_sentiment_summary
from notifier              import bulk_notify
from backend.knowledge_graph import build_graph
from collections           import Counter
import plotly.graph_objects as go
import pandas as pd

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

*,[class*="css"]{font-family:'DM Sans',sans-serif;box-sizing:border-box;}
.stApp{background:#080d18;color:#dde3ef;}
.main .block-container{padding-top:1.2rem;padding-bottom:2rem;max-width:1380px;}
section[data-testid="stSidebar"]{background:#060b14!important;border-right:1px solid #111e35;}

.page-title{font-family:'Syne',sans-serif;font-size:1.65rem;font-weight:800;color:#e8edf8;letter-spacing:-.03em;line-height:1.1;}
.page-sub{font-size:.8rem;color:#3d5070;margin-top:.25rem;}
.sec-hdr{font-family:'Syne',sans-serif;font-size:.72rem;font-weight:700;color:#2d4266;letter-spacing:.12em;text-transform:uppercase;padding-bottom:.35rem;border-bottom:1px solid #111e35;margin-bottom:.8rem;}

.kcard{background:linear-gradient(135deg,#0c1322,#0a1020);border:1px solid #111e35;border-top:2px solid var(--ac,#2563eb);border-radius:12px;padding:1.1rem 1.3rem;position:relative;overflow:hidden;}
.kcard::after{content:'';position:absolute;inset:0;background:radial-gradient(circle at top right,color-mix(in srgb,var(--ac,#2563eb) 8%,transparent),transparent 65%);}
.kcard-label{font-size:.68rem;color:#2d4266;letter-spacing:.09em;text-transform:uppercase;}
.kcard-val{font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#e8edf8;line-height:1;margin:.2rem 0;}
.kcard-sub{font-size:.72rem;color:#2a3a55;}

.seg-card{background:#0c1322;border:1px solid #111e35;border-left:3px solid var(--sc,#2563eb);border-radius:10px;padding:.9rem 1.1rem;margin-bottom:.5rem;}
.seg-title{font-family:'Syne',sans-serif;font-size:.95rem;font-weight:700;color:var(--sc,#2563eb);}
.seg-meta{font-size:.74rem;color:#2d4266;line-height:1.7;margin-top:.35rem;}
.seg-meta b{color:#7a95c0;}

.scheme-card{background:#0c1322;border:1px solid #111e35;border-left:3px solid var(--cc,#2563eb);border-radius:9px;padding:.75rem 1rem;margin-bottom:.45rem;}
.scheme-cat{font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;color:var(--cc,#2563eb);margin-bottom:.15rem;}
.scheme-name{font-weight:600;color:#93b4e8;font-size:.88rem;}
.scheme-desc{font-size:.76rem;color:#2d4266;margin-top:.1rem;}

.pill{display:inline-block;padding:.18rem .7rem;border-radius:20px;font-size:.7rem;font-weight:600;letter-spacing:.03em;margin:2px;}
.pill-pos{background:#032010;color:#4ade80;border:1px solid #14532d;}
.pill-neg{background:#200808;color:#f87171;border:1px solid #7f1d1d;}
.pill-neu{background:#161210;color:#a8a29e;border:1px solid #3a3330;}
.pill-blue{background:#091527;color:#60a5fa;border:1px solid #1e3a5f;}

.fb-row{background:#0c1322;border:1px solid #111e35;border-radius:9px;padding:.75rem 1rem;margin-bottom:.4rem;}
.fb-txt{color:#7a95c0;font-size:.83rem;font-style:italic;margin-top:.3rem;}

.hbar{background:#0c1322;border:1px solid #111e35;border-radius:8px;padding:.55rem .9rem;margin-bottom:.35rem;}
.hbar-lbl{display:flex;justify-content:space-between;align-items:center;margin-bottom:.25rem;}
.hbar-track{background:#111e35;border-radius:4px;height:5px;}
.hbar-fill{height:5px;border-radius:4px;}

.vrow{display:flex;justify-content:space-between;padding:.45rem 0;border-bottom:1px solid #0d1828;}
.vrow-k{font-size:.8rem;color:#2d4266;}
.vrow-v{font-size:.82rem;font-weight:500;color:#c5d3e8;}

[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p{color:#2d4266!important;font-size:.75rem;letter-spacing:.07em;text-transform:uppercase;}

.stSelectbox>div>div,.stTextArea textarea,.stTextInput>div>div>input{background:#0c1322!important;border-color:#111e35!important;color:#c5d3e8!important;}
.stButton>button{background:linear-gradient(135deg,#1a3fa8,#0c6a8a);color:#e8edf8;border:none;border-radius:8px;padding:.45rem 1.4rem;font-family:'DM Sans',sans-serif;font-weight:500;letter-spacing:.03em;transition:all .2s;}
.stButton>button:hover{transform:translateY(-2px);filter:brightness(1.12);}
[data-testid="stDataFrame"]{border:1px solid #111e35!important;border-radius:9px!important;}
hr{border-color:#111e35!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS & HELPERS
# ══════════════════════════════════════════════════════════════════════════════
TYPE_COLORS = {
    "📢 General Announcement":"#3b82f6","🏗️ Development Update":"#f59e0b",
    "📋 Scheme Alert":"#10b981","🗳️ Election Reminder":"#8b5cf6",
    "🚨 Emergency Alert":"#ef4444","💧 Infrastructure Update":"#06b6d4",
}
PRIORITY_COLORS = {"Low":"#22d3ee","Normal":"#3b82f6","High":"#f59e0b","Urgent":"#ef4444"}
CAT_COLORS = {
    "Agriculture":"#10b981","Education":"#3b82f6","Health":"#ec4899",
    "Welfare":"#f59e0b","Pension":"#8b5cf6","Business":"#06b6d4",
    "Housing":"#f97316","Savings":"#14b8a6",
}
SEG_COLORS = ["#3b82f6","#06b6d4","#8b5cf6","#f59e0b","#10b981","#ef4444"]
ALL_SCHEMES = [
    "PM-KISAN","Pradhan Mantri Fasal Bima","Kisan Credit Card",
    "National Scholarship Portal","PM Vidya Lakshmi","Ayushman Bharat PMJAY",
    "Janani Suraksha Yojana","PM Ujjwala Yojana","Beti Bachao Beti Padhao",
    "National Old Age Pension","Atal Pension Yojana","PM MUDRA Yojana",
    "Stand Up India","PM Awas Yojana Urban","Sukanya Samriddhi Yojana",
]

PLOT_BASE = dict(
    plot_bgcolor="#080d18", paper_bgcolor="#080d18",
    font=dict(color="#2d4266",family="DM Sans"),
    margin=dict(l=0,r=0,t=14,b=0),
    xaxis=dict(showgrid=True,gridcolor="#0d1828",tickfont=dict(color="#2d4266"),zeroline=False),
    yaxis=dict(showgrid=True,gridcolor="#0d1828",tickfont=dict(color="#2d4266"),zeroline=False),
    legend=dict(font=dict(color="#3d5070"),bgcolor="rgba(0,0,0,0)"),
)

def get_booths():
    return sorted(set(v["booth_id"] for v in voters_db))

def bar_chart(x, y, colors, h=260, horiz=False):
    fig = go.Figure()
    kw  = dict(marker=dict(color=colors,line=dict(width=0)),
               text=y, textposition="outside",
               textfont=dict(color="#3d5070",size=11))
    if horiz: fig.add_trace(go.Bar(y=x,x=y,orientation="h",**kw))
    else:     fig.add_trace(go.Bar(x=x,y=y,**kw))
    fig.update_layout(**{**PLOT_BASE,"height":h}); return fig

def pie_chart(labels, values, colors, h=250, hole=0.55, ann=""):
    fig = go.Figure(go.Pie(
        labels=labels,values=values,hole=hole,
        marker=dict(colors=colors,line=dict(color="#080d18",width=3)),
        textfont=dict(color="#c5d3e8",size=11)))
    layout = {**PLOT_BASE,"height":h}
    if ann: layout["annotations"]=[dict(text=ann,x=0.5,y=0.5,font=dict(size=14,color="#60a5fa"),showarrow=False)]
    fig.update_layout(**layout); return fig

def kcard(col, label, val, sub="", ac="#2563eb"):
    col.markdown(f"""
    <div class='kcard' style='--ac:{ac};'>
      <div class='kcard-label'>{label}</div>
      <div class='kcard-val' style='color:{ac};'>{val}</div>
      <div class='kcard-sub'>{sub}</div>
    </div>""", unsafe_allow_html=True)

def scheme_card(s, enrolled=False):
    cc  = CAT_COLORS.get(s["category"],"#64748b")
    tag = (" <span style='font-size:.62rem;background:#032010;color:#4ade80;"
           "padding:1px 7px;border-radius:4px;border:1px solid #14532d;'>✓ Enrolled</span>"
           if enrolled else "")
    st.markdown(f"""
    <div class='scheme-card' style='--cc:{cc};'>
      <div class='scheme-cat'>{s['category']}</div>
      <div class='scheme-name'>{s['name']}{tag}</div>
      <div class='scheme-desc'>{s['description']}</div>
    </div>""", unsafe_allow_html=True)

# ── filter voters helper ──────────────────────────────────────────────────────
def filter_voters(mode, booths_list):
    sv = []
    if mode == "🏘️ Booth":
        opts = ["All Booths"] + get_booths()
        fb   = st.selectbox("Booth", opts)
        sv   = voters_db[:] if fb=="All Booths" else [v for v in voters_db if v["booth_id"]==fb]

    elif mode == "👤 Occupation":
        all_occs = sorted(set(v["occupation"] for v in voters_db))
        foccs    = st.multiselect("Occupations", all_occs, default=[all_occs[0]])
        sv       = [v for v in voters_db if v["occupation"] in foccs]
        sb       = st.selectbox("Also filter by Booth", ["All"]+get_booths(), key="occ_b")
        if sb != "All": sv = [v for v in sv if v["booth_id"]==sb]

    elif mode == "🔢 Age Group":
        age_map = {"Youth (18-24)":(18,24),"Young Adult (25-39)":(25,39),
                   "Middle Aged (40-59)":(40,59),"Senior (60+)":(60,120)}
        fg   = st.selectbox("Age Group", list(age_map.keys()))
        lo,hi= age_map[fg]
        sv   = [v for v in voters_db if lo<=v["age"]<=hi]
        sb   = st.selectbox("Also filter by Booth", ["All"]+get_booths(), key="age_b")
        if sb != "All": sv = [v for v in sv if v["booth_id"]==sb]

    elif mode == "♀️ Gender":
        fgen = st.multiselect("Gender(s)",["Male","Female","Other"],default=["Female"])
        sv   = [v for v in voters_db if v["gender"] in fgen]
        sb   = st.selectbox("Also filter by Booth", ["All"]+get_booths(), key="gen_b")
        if sb != "All": sv = [v for v in sv if v["booth_id"]==sb]

    elif mode == "✋ Individual":
        opts   = [f"{v['voter_id']} – {v['name']} ({v['booth_id']})" for v in voters_db]
        picked = st.multiselect("Pick Voters", opts, placeholder="Search by name or ID…")
        pids   = [p.split(" – ")[0] for p in picked]
        sv     = [v for v in voters_db if v["voter_id"] in pids]

    return sv

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:.8rem 0 1.4rem'>
      <div style='font-family:Syne,sans-serif;font-size:1.35rem;font-weight:800;
                  color:#e8edf8;letter-spacing:-.025em;'>🗳️ BoothIQ</div>
      <div style='font-size:.66rem;color:#1e2e48;letter-spacing:.1em;
                  text-transform:uppercase;margin-top:.2rem;'>AI Civic Intelligence v2</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio("NAVIGATE", [
        "📊 Dashboard",
        "👥 Voter Segments",
        "📋 Scheme Recommender",
        "💬 Sentiment Analysis",
        "🔍 Voter Lookup",
        "➕ Add Voter",
        "🔔 Send Notification","🧠 Knowledge Graph",
    ])

    st.markdown("---")
    selected_booth = st.selectbox("SELECT BOOTH", get_booths())
    st.markdown("""
    <div style='position:absolute;bottom:1.2rem;left:0;right:0;
                text-align:center;font-size:.62rem;color:#111e35;'>
      BoothIQ v2.0 · Hackathon Edition
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 – DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("<div class='page-title'>Overview Dashboard</div>"
                "<div class='page-sub'>Live civic intelligence across all booths</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    bv       = [v for v in voters_db if v["booth_id"]==selected_booth]
    gap      = get_booth_scheme_coverage(bv)
    sent_all = get_booth_sentiment_summary(feedback_db) if feedback_db else {}

    c1,c2,c3,c4 = st.columns(4)
    kcard(c1,"Total Voters",    len(voters_db),                         "All registered",         "#2563eb")
    kcard(c2,"Active Booths",   len(get_booths()),                      "Polling units",           "#06b6d4")
    kcard(c3,"Feedback Logged", len(feedback_db),                       "Citizen responses",       "#8b5cf6")
    kcard(c4,"Scheme Gap",      gap["voters_missing_schemes"],          f"{gap['coverage_gap_percent']}% missing","#f59e0b")

    st.markdown("<br>", unsafe_allow_html=True)
    cl,cr = st.columns([1.1,1])
    with cl:
        st.markdown("<div class='sec-hdr'>Voters per Booth</div>", unsafe_allow_html=True)
        bc = {b:sum(1 for v in voters_db if v["booth_id"]==b) for b in get_booths()}
        st.plotly_chart(bar_chart(list(bc.keys()),list(bc.values()),
                                  SEG_COLORS[:len(bc)]), use_container_width=True)
    with cr:
        st.markdown("<div class='sec-hdr'>Gender Distribution</div>", unsafe_allow_html=True)
        gd = dict(Counter(v["gender"] for v in voters_db))
        st.plotly_chart(pie_chart(list(gd.keys()),list(gd.values()),
                                  ["#3b82f6","#ec4899","#06b6d4"]), use_container_width=True)

    cl2,cr2 = st.columns(2)
    with cl2:
        st.markdown("<div class='sec-hdr'>Occupation Breakdown</div>", unsafe_allow_html=True)
        od = dict(Counter(v["occupation"] for v in voters_db))
        st.plotly_chart(bar_chart(list(od.keys()),list(od.values()),
                                  SEG_COLORS[:len(od)],h=240,horiz=True), use_container_width=True)
    with cr2:
        st.markdown("<div class='sec-hdr'>Sentiment Overview</div>", unsafe_allow_html=True)
        if feedback_db:
            sb = sent_all.get("breakdown",{})
            st.plotly_chart(bar_chart(
                ["Positive","Negative","Neutral"],
                [sb.get("Positive",0),sb.get("Negative",0),sb.get("Neutral",0)],
                ["#4ade80","#f87171","#a8a29e"],h=240), use_container_width=True)
        else:
            st.info("No feedback yet.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 – VOTER SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Voter Segments":
    st.markdown(f"<div class='page-title'>AI Voter Segmentation</div>"
                f"<div class='page-sub'>K-Means clustering · Booth {selected_booth}</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    bv = [v for v in voters_db if v["booth_id"]==selected_booth]
    if not bv: st.warning("No voters for this booth."); st.stop()

    segs = segment_voters(bv)
    dist = get_booth_distribution(bv)

    st.markdown("<div class='sec-hdr'>Identified Segments</div>", unsafe_allow_html=True)
    cols = st.columns(len(segs))
    for i,(sid,sd) in enumerate(segs.items()):
        c = SEG_COLORS[i%len(SEG_COLORS)]
        cols[i].markdown(f"""
        <div class='seg-card' style='--sc:{c};'>
          <div style='font-size:.65rem;color:#2d4266;letter-spacing:.07em;text-transform:uppercase;'>{sid}</div>
          <div class='seg-title'>{sd['label']}</div>
          <div style='font-family:Syne,sans-serif;font-size:1.7rem;font-weight:800;color:#e8edf8;line-height:1;margin:.25rem 0;'>{sd['count']}</div>
          <div style='font-size:.68rem;color:#2d4266;'>voters</div>
          <div class='seg-meta'>Avg Age:<b>{sd['avg_age']}</b><br>Income:<b>{sd['income_group']}</b><br>Occ:<b>{sd['dominant_occupation']}</b></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl,cr = st.columns(2)
    with cl:
        st.markdown("<div class='sec-hdr'>Age Groups</div>", unsafe_allow_html=True)
        ag = dist["age_groups"]
        st.plotly_chart(pie_chart(list(ag.keys()),list(ag.values()),
                                  ["#3b82f6","#06b6d4","#8b5cf6","#f59e0b"]), use_container_width=True)
    with cr:
        st.markdown("<div class='sec-hdr'>Scheme Enrollment</div>", unsafe_allow_html=True)
        sc = dist["scheme_coverage"]
        st.plotly_chart(pie_chart(["Enrolled","Not Enrolled"],
                                  [sc["enrolled"],sc["not_enrolled"]],
                                  ["#10b981","#ef4444"],
                                  ann=f"{sc['coverage_percent']}%"), use_container_width=True)

    st.markdown("<div class='sec-hdr'>Booth Voter List</div>", unsafe_allow_html=True)
    df = pd.DataFrame(bv)[["voter_id","name","age","gender","occupation","income","email","phone"]]
    df.columns = ["ID","Name","Age","Gender","Occupation","Income (₹)","Email","Phone"]
    st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 – SCHEME RECOMMENDER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Scheme Recommender":
    st.markdown("<div class='page-title'>Government Scheme Recommender</div>"
                "<div class='page-sub'>AI-powered personalized scheme matching engine</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1,tab2 = st.tabs(["🔎 By Profile","🏘️ Booth Coverage Gap"])

    with tab1:
        cf,cr = st.columns([1,1.5])
        with cf:
            st.markdown("<div class='sec-hdr'>Voter Profile</div>", unsafe_allow_html=True)
            age  = st.slider("Age",18,90,35)
            gen  = st.selectbox("Gender",["Male","Female","Other"])
            occ  = st.selectbox("Occupation",["Farmer","Student","Teacher","Business","Homemaker","Retired","Labour","Govt"])
            inc  = st.number_input("Annual Income (₹)",0,5000000,step=10000,value=80000)
            land = st.checkbox("Owns Agricultural Land")
            btn  = st.button("🔍 Find Schemes", use_container_width=True)
        with cr:
            st.markdown("<div class='sec-hdr'>Recommended Schemes</div>", unsafe_allow_html=True)
            if btn:
                schemes = recommend_schemes(age,occ,int(inc),land,gen)
                if schemes:
                    for s in schemes: scheme_card(s)
                else:
                    st.info("No matching schemes.")
            else:
                st.markdown("<div style='color:#1a2a40;font-size:.83rem;padding:2.5rem;text-align:center;'>"
                            "Fill the profile and click <b>Find Schemes</b></div>", unsafe_allow_html=True)

    with tab2:
        bv  = [v for v in voters_db if v["booth_id"]==selected_booth]
        gap = get_booth_scheme_coverage(bv)
        c1,c2,c3 = st.columns(3)
        kcard(c1,"Total Voters",     gap["total_voters"],            "",                              "#2563eb")
        kcard(c2,"Missing Schemes",  gap["voters_missing_schemes"],  "",                              "#ef4444")
        kcard(c3,"Coverage Gap",     f"{gap['coverage_gap_percent']}%","",                            "#f59e0b")
        st.markdown("<br>", unsafe_allow_html=True)
        if gap["details"]:
            st.markdown("<div class='sec-hdr'>Voters Missing Schemes</div>", unsafe_allow_html=True)
            for d in gap["details"]:
                pills = "".join(f"<span class='pill pill-neg'>{s}</span>" for s in d["missing_schemes"])
                st.markdown(f"""
                <div class='fb-row'>
                  <div style='display:flex;gap:.6rem;align-items:center;flex-wrap:wrap;'>
                    <span style='color:#3b82f6;font-weight:600;font-size:.82rem;min-width:60px;'>{d['voter_id']}</span>
                    <span style='color:#7a95c0;flex:1;font-size:.83rem;'>{d['name']}</span>
                    {pills}
                  </div>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 – SENTIMENT ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💬 Sentiment Analysis":
    st.markdown(f"<div class='page-title'>Sentiment Analysis</div>"
                f"<div class='page-sub'>NLP issue heatmap · Booth {selected_booth}</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab_live,tab_booth = st.tabs(["📝 Live Analyzer","📊 Booth Summary"])

    with tab_live:
        txt = st.text_area("Citizen feedback:",placeholder="e.g. Roads are very bad, no repair done in years...",height=110)
        if st.button("🔍 Analyze") and txt.strip():
            r  = analyze_sentiment(txt)
            s  = r["sentiment"]
            pc = {"Positive":"#4ade80","Negative":"#f87171","Neutral":"#a8a29e"}.get(s,"#a8a29e")
            bc = {"Positive":"pill-pos","Negative":"pill-neg","Neutral":"pill-neu"}.get(s,"pill-neu")
            sc = "#4ade80" if r["score"]>0 else ("#f87171" if r["score"]<0 else "#a8a29e")
            c1,c2,c3 = st.columns(3)
            c1.markdown(f"<div class='kcard' style='--ac:{pc};'><div class='kcard-label'>Sentiment</div><div class='kcard-val'><span class='pill {bc}'>{s}</span></div></div>",unsafe_allow_html=True)
            c2.markdown(f"<div class='kcard' style='--ac:{sc};'><div class='kcard-label'>Score</div><div class='kcard-val' style='color:{sc};'>{r['score']:+.2f}</div></div>",unsafe_allow_html=True)
            c3.markdown(f"<div class='kcard' style='--ac:#06b6d4;'><div class='kcard-label'>Issues</div><div class='kcard-val'>{len(r['issues'])}</div></div>",unsafe_allow_html=True)
            if r["issues"]:
                st.markdown("<br><div class='sec-hdr'>Detected Issues</div>",unsafe_allow_html=True)
                st.markdown("".join(f"<span class='pill pill-blue'>{i}</span>" for i in r["issues"]),unsafe_allow_html=True)

    with tab_booth:
        bf = [f for f in feedback_db if f["booth_id"]==selected_booth]
        if not bf: st.info("No feedback for this booth yet.")
        else:
            sm = get_booth_sentiment_summary(bf)
            bd = sm["breakdown"]
            ov = sm["overall_sentiment"]
            oc = {"Positive":"#4ade80","Negative":"#f87171","Neutral":"#a8a29e"}.get(ov,"#a8a29e")
            c1,c2,c3,c4 = st.columns(4)
            kcard(c1,"Overall",  ov,                      "", oc)
            kcard(c2,"Positive", f"{bd['positive_percent']}%","","#4ade80")
            kcard(c3,"Negative", f"{bd['negative_percent']}%","","#f87171")
            kcard(c4,"Avg Score",f"{sm['average_score']:+.2f}","",
                  "#4ade80" if sm["average_score"]>0 else "#f87171")
            st.markdown("<br>", unsafe_allow_html=True)
            cl,cr = st.columns([1,1.3])
            with cl:
                st.markdown("<div class='sec-hdr'>Issue Severity Heatmap</div>",unsafe_allow_html=True)
                for iss,lvl in sm.get("issue_severity",{}).items():
                    ic={"High":"🔴","Medium":"🟡","Low":"🔵"}.get(lvl,"⚪")
                    w={"High":"82%","Medium":"50%","Low":"22%"}.get(lvl,"10%")
                    c={"High":"#ef4444","Medium":"#f59e0b","Low":"#22d3ee"}.get(lvl,"#64748b")
                    lc={"High":"#f87171","Medium":"#fbbf24","Low":"#22d3ee"}.get(lvl,"#64748b")
                    st.markdown(f"""
                    <div class='hbar'>
                      <div class='hbar-lbl'>
                        <span style='color:#7a95c0;font-size:.8rem;text-transform:capitalize;'>{ic} {iss}</span>
                        <span style='color:{lc};font-size:.75rem;font-weight:600;'>{lvl}</span>
                      </div>
                      <div class='hbar-track'><div class='hbar-fill' style='width:{w};background:{c};'></div></div>
                    </div>""",unsafe_allow_html=True)
            with cr:
                st.markdown("<div class='sec-hdr'>Sentiment Breakdown</div>",unsafe_allow_html=True)
                st.plotly_chart(bar_chart(["Positive","Negative","Neutral"],
                    [bd["Positive"],bd["Negative"],bd["Neutral"]],
                    ["#4ade80","#f87171","#a8a29e"],h=260),use_container_width=True)

            st.markdown("<div class='sec-hdr'>All Feedback</div>",unsafe_allow_html=True)
            for f in bf:
                s  = f["sentiment"]
                bc = {"Positive":"pill-pos","Negative":"pill-neg","Neutral":"pill-neu"}.get(s,"pill-neu")
                sc = "#4ade80" if f.get("score",0)>0 else ("#f87171" if f.get("score",0)<0 else "#a8a29e")
                ip = "".join(f"<span class='pill pill-blue'>{i}</span>" for i in f.get("issues",[]))
                st.markdown(f"""
                <div class='fb-row'>
                  <div style='display:flex;gap:.6rem;align-items:center;margin-bottom:.3rem;flex-wrap:wrap;'>
                    <span class='pill {bc}'>{s}</span>
                    <span style='color:{sc};font-size:.72rem;'>{f.get('score',0):+.2f}</span>
                    <span style='color:#1a2a40;font-size:.72rem;'>{f.get('voter_id','')}</span>
                    {ip}
                  </div>
                  <div class='fb-txt'>"{f['text']}"</div>
                </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 – VOTER LOOKUP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Voter Lookup":
    st.markdown("<div class='page-title'>Voter Lookup</div>"
                "<div class='page-sub'>Full profile · schemes · enrollment status</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    sel   = st.selectbox("Select Voter",[f"{v['voter_id']} – {v['name']}" for v in voters_db])
    voter = next((v for v in voters_db if v["voter_id"]==sel.split(" – ")[0]),None)

    if voter:
        ci,cs = st.columns([1,1.5])
        with ci:
            st.markdown("<div class='sec-hdr'>Profile</div>",unsafe_allow_html=True)
            for k,v in [("Voter ID",voter["voter_id"]),("Name",voter["name"]),
                        ("Age",voter["age"]),("Gender",voter["gender"]),
                        ("Occupation",voter["occupation"]),("Income",f"₹{voter['income']:,}"),
                        ("Booth",voter["booth_id"]),("Owns Land","Yes" if voter["land_ownership"] else "No"),
                        ("Email",voter.get("email","—")),("Phone",voter.get("phone","—"))]:
                st.markdown(f"<div class='vrow'><span class='vrow-k'>{k}</span><span class='vrow-v'>{v}</span></div>",unsafe_allow_html=True)
            st.markdown("<br><div class='sec-hdr'>Currently Enrolled</div>",unsafe_allow_html=True)
            enrolled = voter["schemes_enrolled"]
            if enrolled:
                st.markdown("".join(f"<span class='pill pill-pos'>{s}</span>" for s in enrolled),unsafe_allow_html=True)
            else:
                st.markdown("<span style='color:#1a2a40;font-size:.8rem;'>No schemes enrolled</span>",unsafe_allow_html=True)
        with cs:
            st.markdown("<div class='sec-hdr'>Recommended Schemes</div>",unsafe_allow_html=True)
            schemes = recommend_schemes(voter["age"],voter["occupation"],voter["income"],voter["land_ownership"],voter["gender"])
            if schemes:
                for s in schemes: scheme_card(s, s["name"] in voter["schemes_enrolled"])
            else:
                st.info("No matching schemes.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 – ADD VOTER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Voter":
    if "voter_added"  not in st.session_state: st.session_state.voter_added  = False
    if "last_added"   not in st.session_state: st.session_state.last_added   = None

    st.markdown("<div class='page-title'>Add New Voter</div>"
                "<div class='page-sub'>Register a voter and instantly see scheme eligibility</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.voter_added and st.session_state.last_added:
        v = st.session_state.last_added
        st.markdown(f"""
        <div style='background:#032010;border:1px solid #14532d;border-radius:10px;
                    padding:1rem 1.3rem;margin-bottom:1.2rem;display:flex;align-items:center;gap:1rem;'>
          <span style='font-size:1.5rem;'>✅</span>
          <div>
            <div style='font-family:Syne,sans-serif;font-weight:700;color:#4ade80;font-size:.95rem;'>Voter Added Successfully!</div>
            <div style='color:#2d6a4f;font-size:.8rem;margin-top:.15rem;'>{v['name']} · {v['voter_id']} · Booth {v['booth_id']}</div>
          </div>
        </div>""",unsafe_allow_html=True)

    cf,cp = st.columns([1.2,1])
    with cf:
        st.markdown("<div class='sec-hdr'>Personal Details</div>",unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        f_name = c1.text_input("Full Name *",placeholder="e.g. Ramesh Kumar")
        f_vid  = c2.text_input("Voter ID *",value=f"V{len(voters_db)+1:03d}")
        c3,c4,c5 = st.columns(3)
        f_age    = c3.number_input("Age *",18,110,30)
        f_gender = c4.selectbox("Gender *",["Male","Female","Other"])
        f_booth_sel = c5.selectbox("Booth *",get_booths()+["New Booth"])
        f_booth  = st.text_input("New Booth ID",placeholder="e.g. B04") if f_booth_sel=="New Booth" else f_booth_sel
        c6,c7 = st.columns(2)
        f_occ    = c6.selectbox("Occupation *",["Farmer","Student","Teacher","Business","Homemaker","Retired","Labour","Govt","Other"])
        f_income = c7.number_input("Annual Income (₹)",0,10000000,step=5000,value=0)
        f_land   = st.checkbox("Owns Agricultural Land")
        c8,c9 = st.columns(2)
        f_email  = c8.text_input("Email",placeholder="voter@example.com")
        f_phone  = c9.text_input("Phone",placeholder="+91XXXXXXXXXX")
        st.markdown("<div class='sec-hdr' style='margin-top:1rem;'>Scheme Enrollment</div>",unsafe_allow_html=True)
        f_schemes = st.multiselect("Currently enrolled schemes (optional)",options=ALL_SCHEMES,placeholder="Select schemes…")
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.button("➕ Register Voter",use_container_width=True)

    with cp:
        st.markdown("<div class='sec-hdr'>Live Preview</div>",unsafe_allow_html=True)
        st.markdown(f"""
        <div class='kcard' style='--ac:#2563eb;margin-bottom:.8rem;'>
          <div style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#e8edf8;margin-bottom:.6rem;'>
            {f_name or "— Name —"}
          </div>
          <div style='display:grid;grid-template-columns:1fr 1fr;gap:.3rem .8rem;'>
            {"".join(f"<div style='font-size:.73rem;color:#2d4266;'>{k}</div><div style='font-size:.73rem;color:#7a95c0;font-weight:500;'>{v}</div>"
                     for k,v in [("Voter ID",f_vid or "—"),("Age",f_age),("Gender",f_gender),
                                  ("Occupation",f_occ),("Booth",f_booth or "—"),
                                  ("Income",f"₹{f_income:,}"),("Owns Land","Yes" if f_land else "No")])}
          </div>
        </div>""",unsafe_allow_html=True)
        st.markdown("<div class='sec-hdr'>Eligible Schemes Preview</div>",unsafe_allow_html=True)
        if f_name and f_occ:
            for s in recommend_schemes(f_age,f_occ,int(f_income),f_land,f_gender):
                cc = CAT_COLORS.get(s["category"],"#64748b")
                st.markdown(f"<div class='scheme-card' style='--cc:{cc};padding:.5rem .8rem;'><div class='scheme-cat'>{s['category']}</div><div class='scheme-name' style='font-size:.82rem;'>{s['name']}</div></div>",unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#1a2a40;font-size:.8rem;'>Fill the form to see eligible schemes.</div>",unsafe_allow_html=True)

    if submit:
        errors = []
        if not f_name.strip():     errors.append("Full Name is required.")
        if not f_vid.strip():      errors.append("Voter ID is required.")
        if any(v["voter_id"]==f_vid.strip() for v in voters_db): errors.append(f"Voter ID '{f_vid}' already exists.")
        if not f_booth or not f_booth.strip(): errors.append("Booth ID is required.")
        if errors:
            for e in errors: st.error(e)
        else:
            new_v = {"voter_id":f_vid.strip(),"name":f_name.strip(),"age":int(f_age),
                     "gender":f_gender,"occupation":f_occ,"income":int(f_income),
                     "booth_id":f_booth.strip(),"land_ownership":f_land,
                     "schemes_enrolled":f_schemes,"email":f_email.strip(),"phone":f_phone.strip()}
            voters_db.append(new_v)
            st.session_state.voter_added = True
            st.session_state.last_added  = new_v
            st.rerun()

    st.markdown("<br><div class='sec-hdr'>All Registered Voters</div>",unsafe_allow_html=True)
    df = pd.DataFrame(voters_db)[["voter_id","name","age","gender","occupation","income","booth_id","email","phone"]]
    df.columns = ["ID","Name","Age","Gender","Occupation","Income (₹)","Booth","Email","Phone"]
    st.dataframe(df.sort_values("ID").reset_index(drop=True),use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 7 – SEND NOTIFICATION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔔 Send Notification":
    for key,default in [("notifications_log",[]),("notif_sent",False),
                        ("last_notif",None),("send_results",None)]:
        if key not in st.session_state: st.session_state[key] = default

    st.markdown("<div class='page-title'>Send Notification</div>"
                "<div class='page-sub'>Filter voters · compose · deliver via Email &amp; SMS</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # result banner
    if st.session_state.notif_sent and st.session_state.last_notif:
        n  = st.session_state.last_notif
        r  = st.session_state.send_results or {}
        em = r.get("email",{}); sm = r.get("sms",{})
        st.markdown(f"""
        <div style='background:#032010;border:1px solid #14532d;border-radius:10px;
                    padding:1rem 1.4rem;margin-bottom:1.2rem;'>
          <div style='font-family:Syne,sans-serif;font-weight:700;color:#4ade80;font-size:1rem;margin-bottom:.5rem;'>🔔 Notification Dispatched!</div>
          <div style='display:flex;gap:2rem;flex-wrap:wrap;'>
            <div style='font-size:.8rem;color:#2d6a4f;'>📧 Email — ✅ {em.get('sent',0)} sent | ❌ {em.get('failed',0)} failed</div>
            <div style='font-size:.8rem;color:#2d6a4f;'>📱 SMS — ✅ {sm.get('sent',0)} sent | ❌ {sm.get('failed',0)} failed</div>
            <div style='font-size:.78rem;color:#1a4231;'>Sent at {n['sent_at']}</div>
          </div>
        </div>""",unsafe_allow_html=True)
        st.session_state.notif_sent = False

    tab_compose,tab_config,tab_log = st.tabs(["📝 Compose & Send","⚙️ Channel Config","📋 Log"])

    # ── TAB 1: COMPOSE ────────────────────────────────────────────────────────
    with tab_compose:
        cl,cr = st.columns([1.15,1])
        with cl:
            st.markdown("<div class='sec-hdr'>Step 1 · Target Recipients</div>",unsafe_allow_html=True)
            filter_mode = st.radio("Filter by:",["🏘️ Booth","👤 Occupation","🔢 Age Group","♀️ Gender","✋ Individual"],horizontal=True)
            selected_voters = filter_voters(filter_mode, get_booths())

            st.markdown("<br><div class='sec-hdr'>Step 2 · Delivery Channels</div>",unsafe_allow_html=True)
            cc1,cc2 = st.columns(2)
            via_email = cc1.checkbox("📧 Email",value=True)
            via_sms   = cc2.checkbox("📱 SMS",  value=False)

            st.markdown("<br><div class='sec-hdr'>Step 3 · Message</div>",unsafe_allow_html=True)
            notif_type  = st.selectbox("Type",list(TYPE_COLORS.keys()))
            priority    = st.select_slider("Priority",["Low","Normal","High","Urgent"],value="Normal")
            notif_title = st.text_input("Title *",placeholder="e.g. New drainage work completed in your area")
            notif_body  = st.text_area("Body *",placeholder="e.g. Dear resident, the drainage repair work has been completed…",height=110)
            notif_link  = st.text_input("Reference Link (optional)",placeholder="https://...")
            st.markdown("<br>", unsafe_allow_html=True)
            send_btn = st.button("🔔 Send Now",use_container_width=True)

        with cr:
            nc = TYPE_COLORS.get(notif_type,"#3b82f6")
            pc = PRIORITY_COLORS.get(priority,"#3b82f6")
            st.markdown("<div class='sec-hdr'>Preview</div>",unsafe_allow_html=True)
            st.markdown(f"""
            <div style='background:#0c1322;border:1px solid #111e35;border-left:4px solid {nc};border-radius:12px;padding:1.1rem 1.2rem;margin-bottom:.9rem;'>
              <div style='display:flex;justify-content:space-between;margin-bottom:.45rem;'>
                <span style='font-size:.63rem;color:{nc};letter-spacing:.09em;text-transform:uppercase;font-weight:700;'>{notif_type}</span>
                <span style='font-size:.63rem;background:{pc}28;color:{pc};padding:2px 9px;border-radius:10px;border:1px solid {pc}55;font-weight:600;'>{priority}</span>
              </div>
              <div style='font-family:Syne,sans-serif;font-size:.96rem;font-weight:700;color:#e8edf8;line-height:1.3;margin-bottom:.45rem;'>{notif_title or "— Title —"}</div>
              <div style='font-size:.77rem;color:#7a95c0;line-height:1.55;'>{notif_body or "— Body —"}</div>
              {f'<div style="margin-top:.5rem;"><a href="{notif_link}" style="color:{nc};font-size:.72rem;">🔗 {notif_link}</a></div>' if notif_link else ""}
            </div>""",unsafe_allow_html=True)

            cnt   = len(selected_voters)
            cnt_c = "#4ade80" if cnt>0 else "#f87171"
            booths_str = ", ".join(sorted(set(v["booth_id"] for v in selected_voters))) or "—"
            kcard(cr, "Recipients", cnt, f"Booths: {booths_str}", cnt_c)

            if via_email: st.markdown("<span class='pill pill-blue'>📧 Email</span>",unsafe_allow_html=True)
            if via_sms:   st.markdown("<span class='pill' style='background:#1a0e2e;color:#a78bfa;border:1px solid #5b21b6;'>📱 SMS</span>",unsafe_allow_html=True)

            if selected_voters:
                st.markdown("<br><div style='font-size:.65rem;color:#1e2e48;letter-spacing:.07em;text-transform:uppercase;margin-bottom:.35rem;'>RECIPIENTS</div>",unsafe_allow_html=True)
                for v in selected_voters[:8]:
                    occ_c={"Farmer":"#10b981","Student":"#3b82f6","Teacher":"#8b5cf6",
                           "Business":"#f59e0b","Homemaker":"#ec4899","Retired":"#06b6d4"}.get(v["occupation"],"#64748b")
                    em_ic="📧" if v.get("email") else ""
                    ph_ic="📱" if v.get("phone") else ""
                    st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:.5rem;padding:.3rem 0;border-bottom:1px solid #0d1828;'>
                      <span style='font-size:.67rem;color:#1a2a40;min-width:42px;'>{v['voter_id']}</span>
                      <span style='font-size:.76rem;color:#7a95c0;flex:1;'>{v['name']}</span>
                      <span style='font-size:.64rem;color:{occ_c};'>{v['occupation']}</span>
                      <span style='font-size:.64rem;'>{em_ic}{ph_ic}</span>
                    </div>""",unsafe_allow_html=True)
                if cnt>8:
                    st.markdown(f"<div style='font-size:.7rem;color:#1e2e48;text-align:center;margin-top:.4rem;'>+ {cnt-8} more</div>",unsafe_allow_html=True)

        if send_btn:
            errors=[]
            if not notif_title.strip(): errors.append("Title is required.")
            if not notif_body.strip():  errors.append("Body is required.")
            if not selected_voters:     errors.append("No voters match the filter.")
            if not via_email and not via_sms: errors.append("Select at least one channel.")
            if errors:
                for e in errors: st.error(e)
            else:
                with st.spinner(f"Sending to {len(selected_voters)} voter(s)…"):
                    results = bulk_notify(
                        voters=selected_voters,title=notif_title.strip(),body=notif_body.strip(),
                        notif_type=notif_type,priority=priority,link=notif_link.strip(),
                        via_email=via_email,via_sms=via_sms)
                record = {
                    "id":f"N{len(st.session_state.notifications_log)+1:03d}",
                    "type":notif_type,"title":notif_title.strip(),"body":notif_body.strip(),
                    "priority":priority,"filter_mode":filter_mode,"via_email":via_email,"via_sms":via_sms,
                    "recipient_count":len(selected_voters),
                    "booths":sorted(set(v["booth_id"] for v in selected_voters)),
                    "email_sent":results["email"]["sent"],"email_failed":results["email"]["failed"],
                    "sms_sent":results["sms"]["sent"],"sms_failed":results["sms"]["failed"],
                    "sent_at":datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
                }
                st.session_state.notifications_log.insert(0,record)
                st.session_state.notif_sent   = True
                st.session_state.last_notif   = record
                st.session_state.send_results = results
                failed_list = [r for r in results["email"]["results"]+results["sms"]["results"] if not r["success"]]
                if failed_list:
                    st.warning(f"{len(failed_list)} failure(s):")
                    for f_ in failed_list[:5]: st.caption(f"❌ {f_['voter_id']} — {f_['error']}")
                st.rerun()

    # ── TAB 2: CHANNEL CONFIG ─────────────────────────────────────────────────
    with tab_config:
        import smtplib
        st.markdown("<div class='sec-hdr'>📧 Gmail SMTP Setup</div>",unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#0c1322;border:1px solid #111e35;border-radius:9px;padding:1rem 1.2rem;margin-bottom:1rem;font-size:.81rem;color:#7a95c0;line-height:1.85;'>
          <b style='color:#93b4e8;'>Setup steps:</b><br>
          1. Enable <b>2-Factor Auth</b> on your Gmail account<br>
          2. Go to <a href='https://myaccount.google.com/apppasswords' style='color:#3b82f6;'>myaccount.google.com/apppasswords</a> → create App Password for "Mail"<br>
          3. Set before running Streamlit (Windows):<br>
          <code style='color:#4ade80;background:#0a1a0a;padding:2px 6px;border-radius:4px;display:inline-block;margin-top:4px;'>
            set BOOTHIQ_EMAIL=you@gmail.com<br>
            set BOOTHIQ_EMAIL_PWD=xxxx xxxx xxxx xxxx
          </code>
        </div>""",unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        c1.text_input("Gmail Address",value=os.getenv("BOOTHIQ_EMAIL","not set"),disabled=True)
        c2.text_input("App Password",value="●●●●●●●●" if os.getenv("BOOTHIQ_EMAIL_PWD") else "not set",type="password",disabled=True)
        if st.button("🔌 Test Email Connection"):
            try:
                with smtplib.SMTP("smtp.gmail.com",587) as s:
                    s.ehlo(); s.starttls()
                    s.login(os.getenv("BOOTHIQ_EMAIL",""),os.getenv("BOOTHIQ_EMAIL_PWD",""))
                st.success("✅ Gmail connected!")
            except Exception as e:
                st.error(f"❌ {e}")

        st.markdown("<br><div class='sec-hdr'>📱 Twilio SMS Setup</div>",unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#0c1322;border:1px solid #111e35;border-radius:9px;padding:1rem 1.2rem;margin-bottom:1rem;font-size:.81rem;color:#7a95c0;line-height:1.85;'>
          <b style='color:#93b4e8;'>Setup steps:</b><br>
          1. Sign up free at <a href='https://www.twilio.com' style='color:#8b5cf6;'>twilio.com</a><br>
          2. Get <b>Account SID</b> and <b>Auth Token</b> from Console<br>
          3. Get a Twilio phone number<br>
          4. Install: <code style='color:#4ade80;'>pip install twilio</code><br>
          5. Set environment variables:<br>
          <code style='color:#4ade80;background:#0a1a0a;padding:2px 6px;border-radius:4px;display:inline-block;margin-top:4px;'>
            set TWILIO_ACCOUNT_SID=ACxxxxxxxx<br>
            set TWILIO_AUTH_TOKEN=your_token<br>
            set TWILIO_FROM_NUMBER=+1XXXXXXXXXX
          </code>
        </div>""",unsafe_allow_html=True)
        c3,c4,c5 = st.columns(3)
        c3.text_input("Account SID",value=os.getenv("TWILIO_ACCOUNT_SID","not set"),disabled=True)
        c4.text_input("Auth Token",value="●●●●●●●●" if os.getenv("TWILIO_AUTH_TOKEN") else "not set",type="password",disabled=True)
        c5.text_input("From Number",value=os.getenv("TWILIO_FROM_NUMBER","not set"),disabled=True)
        st.info("💡 After setting environment variables, restart Streamlit.")

    # ── TAB 3: LOG ────────────────────────────────────────────────────────────
    with tab_log:
        log = st.session_state.notifications_log
        if not log:
            st.markdown("<div style='text-align:center;padding:3.5rem;color:#1a2a40;'><div style='font-size:2rem;margin-bottom:.8rem;'>🔔</div><div style='font-size:.85rem;'>No notifications sent yet.</div></div>",unsafe_allow_html=True)
        else:
            c1,c2,c3,c4 = st.columns(4)
            kcard(c1,"Total Sent",    len(log),                                   "","#2563eb")
            kcard(c2,"Total Reached", sum(n["recipient_count"] for n in log),      "","#10b981")
            kcard(c3,"Emails Sent",   sum(n.get("email_sent",0) for n in log),     "","#3b82f6")
            kcard(c4,"SMS Sent",      sum(n.get("sms_sent",0)   for n in log),     "","#8b5cf6")
            st.markdown("<br>", unsafe_allow_html=True)
            for n in log:
                nc = TYPE_COLORS.get(n["type"],"#3b82f6")
                pc = PRIORITY_COLORS.get(n["priority"],"#3b82f6")
                ch = ""
                if n.get("via_email"):
                    ef = n.get("email_failed",0)
                    ch += f"<span class='pill pill-blue'>📧 {n.get('email_sent',0)}{' / ❌'+str(ef) if ef else ''}</span> "
                if n.get("via_sms"):
                    sf = n.get("sms_failed",0)
                    ch += f"<span class='pill' style='background:#1a0e2e;color:#a78bfa;border:1px solid #5b21b6;'>📱 {n.get('sms_sent',0)}{' / ❌'+str(sf) if sf else ''}</span>"
                st.markdown(f"""
                <div style='background:#0c1322;border:1px solid #111e35;border-left:3px solid {nc};border-radius:10px;padding:.9rem 1.1rem;margin-bottom:.55rem;'>
                  <div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem;'>
                    <div style='flex:1;'>
                      <div style='display:flex;gap:.4rem;align-items:center;flex-wrap:wrap;margin-bottom:.3rem;'>
                        <span style='font-size:.62rem;color:{nc};letter-spacing:.07em;text-transform:uppercase;font-weight:700;'>{n['type']}</span>
                        <span style='font-size:.61rem;background:{pc}28;color:{pc};padding:1px 8px;border-radius:8px;border:1px solid {pc}44;'>{n['priority']}</span>
                        <span style='font-size:.61rem;color:#1e2e48;'>{n['id']} · {n['sent_at']}</span>
                      </div>
                      <div style='font-family:Syne,sans-serif;font-size:.88rem;font-weight:700;color:#c5d3e8;margin-bottom:.22rem;'>{n['title']}</div>
                      <div style='font-size:.74rem;color:#3d5070;margin-bottom:.35rem;'>{n['body'][:130]}{'...' if len(n['body'])>130 else ''}</div>
                      <div style='font-size:.66rem;color:#1e2e48;margin-bottom:.3rem;'>Filter: {n['filter_mode']} · Booths: {', '.join(n['booths'])}</div>
                      {ch}
                    </div>
                    <div style='text-align:right;min-width:60px;'>
                      <div style='font-family:Syne,sans-serif;font-size:1.45rem;font-weight:800;color:#e8edf8;'>{n['recipient_count']}</div>
                      <div style='font-size:.63rem;color:#1e2e48;'>voters</div>
                    </div>
                  </div>
                </div>""",unsafe_allow_html=True)
elif page == "🧠 Knowledge Graph":

    st.markdown(
        "<div class='page-title'>Civic Knowledge Graph</div>"
        "<div class='page-sub'>Relationships between voters, booths and schemes</div>",
        unsafe_allow_html=True
    )

    import networkx as nx
    from pyvis.network import Network
    import streamlit.components.v1 as components

    G = build_graph(voters_db)

    net = Network(height="600px", width="100%", bgcolor="#080d18", font_color="white")

    for node in G.nodes(data=True):
        net.add_node(node[0], label=node[0])

    for edge in G.edges(data=True):
        net.add_edge(edge[0], edge[1])

    net.save_graph("graph.html")

    HtmlFile = open("graph.html", "r", encoding="utf-8")
    components.html(HtmlFile.read(), height=600)