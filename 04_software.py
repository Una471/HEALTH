"""
Botswana General Hospital - HOSPITAL MANAGEMENT SYSTEM
Daily operational tool for staff. CLEAR TEXT COLORS.
Run: streamlit run 04_software.py --server.port 8502
"""

import streamlit as st

# Respect report links even when Streamlit Cloud starts this file directly.
if st.query_params.get("view") == "dashboard":
    import runpy
    from pathlib import Path
    runpy.run_path(str(Path(__file__).resolve().parent / "03_dashboard.py"), run_name="__main__")
    st.stop()
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from pathlib import Path
from datetime import datetime, date, timedelta

BASE_DIR = Path(__file__).resolve().parent


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Momo+Trust+Display&family=Red+Hat+Display:wght@500;600;700;800&family=Stack+Sans+Text:wght@400;500;600;700&display=swap');
:root{--forest:#123e2b;--green:#2f742d;--leaf:#78a934;--cream:#fbf8f1;--sage:#eef4e7;--ink:#10251b;--muted:#5c685f;--line:#dfe7dc;}
html,body,[class*="css"],input,button,textarea,select{font-family:'DM Sans',sans-serif!important;color:var(--ink)}
.stApp{background:#fff}.block-container{max-width:1180px;padding:1.2rem 2.4rem 3rem}h1,h2,h3,h4,p,label{color:var(--ink)}
.brandbar{display:flex;align-items:center;justify-content:space-between;padding:.45rem 0 1rem}.brand{display:flex;align-items:center;gap:.65rem}.leafmark{position:relative;width:38px;height:34px}.leafmark i{position:absolute;width:21px;height:30px;background:var(--leaf);border-radius:100% 0 100% 0;transform:rotate(-35deg);left:3px;top:2px}.leafmark i:last-child{left:16px;transform:scaleX(-1) rotate(-35deg);background:#4f8a2f}.brand strong{font-size:1.18rem;letter-spacing:-.04em;color:#123e2b!important}.brand strong span{color:#4f8a2f!important}.brand small{display:block;color:#526157!important;font-size:.62rem;margin-top:-.1rem}.brandmeta{font-size:.74rem;color:#687269;letter-spacing:.06em;text-transform:uppercase;font-weight:700}
.health-hero{min-height:390px;border-radius:4px;overflow:hidden;background-size:cover;background-position:center;display:flex;align-items:center;padding:3.2rem 3.5rem;margin-bottom:1.3rem}.hero-copy{max-width:510px}.hero-copy .eyebrow{color:var(--green);font-size:.9rem;font-weight:700}.hero-copy h1{font-size:3.25rem;line-height:1.04;letter-spacing:-.065em;margin:.55rem 0 1rem;color:#0a3424}.hero-copy p{max-width:430px;font-size:1rem;line-height:1.65;color:#263d31}.hero-cta{display:inline-block;background:var(--green);color:#fff!important;border-radius:7px;padding:.75rem 1.25rem;font-size:.78rem;font-weight:700;margin-top:.4rem;text-decoration:none!important;cursor:pointer;transition:transform .18s ease,background .18s ease}.hero-cta:hover{background:#245f27;transform:translateY(-2px)}.hero-cta:focus{outline:3px solid rgba(74,126,35,.3);outline-offset:3px}html{scroll-behavior:smooth}.workspace-anchor{scroll-margin-top:88px}
.trust-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;background:#f7f9f2;padding:1.1rem 1.25rem;border-radius:8px;margin:0 0 1.5rem}.trust-item{display:flex;gap:.75rem;align-items:center}.trust-icon{width:40px;height:40px;display:grid;place-items:center;border-radius:50%;background:#e9f2dd;color:var(--green);font-size:1rem;font-weight:800}.trust-item b{display:block;font-size:.76rem}.trust-item span{display:block;font-size:.68rem;color:var(--muted);margin-top:.15rem}
.care-panel{display:grid;grid-template-columns:.9fr 1.1fr;gap:2.5rem;align-items:center;margin:1.8rem 0 2rem}.care-copy .eyebrow{color:var(--green);font-size:.67rem;letter-spacing:.12em;font-weight:700}.care-copy h2{font-size:2rem;line-height:1.12;letter-spacing:-.05em;margin:.5rem 0 .8rem}.care-copy p{color:var(--muted);font-size:.82rem;line-height:1.7;max-width:430px}.care-photo{height:230px;background-size:cover;background-position:center;border-radius:14px}
.nav-label{text-align:center;color:var(--green);font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;font-weight:700;margin:.6rem 0 .45rem}div[data-testid="stRadio"]>div{justify-content:center;gap:.25rem;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:.35rem 0;margin-bottom:1.35rem}div[data-testid="stRadio"] label{padding:.6rem .9rem;margin:0!important;border-radius:6px}div[data-testid="stRadio"] label:has(input:checked){background:var(--green)}div[data-testid="stRadio"] label p{font-size:.75rem;font-weight:600;white-space:nowrap;color:#35483c!important}div[data-testid="stRadio"] label:has(input:checked) p{color:#fff!important}div[data-testid="stRadio"] div[role="radiogroup"]>label>div:first-child{display:none}
.topbar{background:var(--cream);padding:1.7rem 2rem;border-radius:12px;margin-bottom:1.2rem;border-left:5px solid var(--green)}.topbar h1{margin:0;font-size:1.8rem;letter-spacing:-.045em;color:var(--forest)}.topbar p{margin:.4rem 0 0;color:var(--muted);font-size:.83rem}
.kcard{background:#f8faf5;border-radius:12px;padding:1.15rem 1.3rem;border:1px solid var(--line);margin-bottom:.3rem;min-height:125px}.kcard.red{background:#fff2ee;border-color:#efc8bf}.kcard.orange{background:#fff8e8;border-color:#ead9a7}.kcard.green{background:#eaf4df;border-color:#cadaaf}.kcard.blue{background:#edf4ec;border-color:#cbdcca}.kval{font-size:1.8rem;font-weight:700;color:var(--forest)}.klbl{font-size:.68rem;text-transform:uppercase;letter-spacing:1.25px;color:#385542;margin-top:.3rem;font-weight:700}.ksub{font-size:.74rem;color:var(--muted);margin-top:.3rem}
.result-card{border-radius:14px;padding:1.8rem;margin:1rem 0;border:1px solid;text-align:center}.result-card.green{background:#eaf4df;border-color:#8bb465;color:#1d5226}.result-card.orange{background:#fff6df;border-color:#d7ad52;color:#744d00}.result-card.red{background:#fff0ec;border-color:#d99b8c;color:#812d20}.alert-box{border-radius:10px;padding:1rem;margin:.5rem 0;border-left:5px solid}.alert-box.red{background:#fff0ec;border-color:#b94a3a;color:#72271d}.alert-box.orange{background:#fff6df;border-color:#b77b16;color:#684609}.alert-box.green{background:#edf6e5;border-color:#4f8a2f;color:#214c22}
section[data-testid="stSidebar"]{display:none!important}.stTextInput input,.stNumberInput input,.stTextArea textarea{background:#fff!important;color:var(--ink)!important;border:1px solid #cfd9cd!important;border-radius:7px!important}.stSelectbox div[data-baseweb="select"]>div{background:#fff!important;color:var(--ink)!important;border-color:#cfd9cd!important;border-radius:7px!important}.stButton>button{background:var(--green);color:#fff;border:0;border-radius:7px;padding:.68rem 1.4rem;font-weight:700;width:100%}.stButton>button *{color:#fff!important}.stButton>button:hover{background:var(--forest);color:#fff}div[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px;overflow:hidden}hr{border-color:var(--line)!important}#MainMenu,footer,header{visibility:hidden}
@media(max-width:850px){.block-container{padding:1rem}.health-hero{padding:2rem 1.3rem;background-position:62% center}.hero-copy{max-width:65%}.hero-copy h1{font-size:2rem}.trust-strip{grid-template-columns:1fr 1fr}.care-panel{grid-template-columns:1fr;gap:1rem}.brandmeta{display:none}div[data-testid="stRadio"]>div{justify-content:flex-start;overflow-x:auto}}
#MainMenu,footer,header{visibility:hidden;}
/* Portfolio typography: expressive brand, editorial headings, highly legible UI. */
html,body,[class*="css"],p,label,input,button,select,textarea{font-family:'Stack Sans Text','Segoe UI',sans-serif!important}
h1,h2,h3,h4{font-family:'Red Hat Display','Segoe UI',sans-serif!important;letter-spacing:-.035em}
.brand-name,.brand strong,.logo-text{font-family:'Momo Trust Display','Red Hat Display',sans-serif!important}
.hero h1,.hero-copy h1{font-family:'Red Hat Display','Segoe UI',sans-serif!important;font-weight:700;letter-spacing:-.055em}
.metric-value,.kval,[data-testid="stMetricValue"]{font-family:'Red Hat Display','Segoe UI',sans-serif!important;font-variant-numeric:tabular-nums}
button,div[data-testid="stRadio"] label p,.eyebrow,.nav-label{font-family:'Stack Sans Text','Segoe UI',sans-serif!important}
.health-hero{min-height:285px}.health-hero .hero-copy h1{font-size:2.65rem}.care-panel{display:grid!important;grid-template-columns:.9fr 1.1fr;gap:1.2rem;padding:1rem 0;margin:.7rem 0}.care-panel .care-copy{padding:.8rem 0}.care-panel .care-copy h2{font-size:1.65rem;margin:.35rem 0}.care-panel .care-copy p{font-size:.78rem;line-height:1.55;max-width:480px}.care-panel .care-photo{min-height:170px;background-position:center;border-radius:10px}.nav-label{margin-top:.55rem}.workspace-note{display:flex;justify-content:space-between;gap:1.2rem;align-items:center;background:#f0f6e9;border-left:4px solid var(--green);padding:.8rem 1rem;margin:.2rem 0 .85rem}.workspace-note b{font-size:.78rem}.workspace-note span{font-size:.72rem;color:var(--muted)}div[data-testid="stRadio"]{position:sticky;top:0;z-index:50;background:rgba(251,248,241,.96);padding:.35rem 0;backdrop-filter:blur(10px)}input:focus,button:focus,[data-baseweb="select"]:focus-within{outline:3px solid rgba(74,126,35,.23)!important;outline-offset:2px}.stButton>button{min-height:44px}.data-hint{font-size:.72rem;color:var(--muted);margin:.2rem 0 .8rem}@media(max-width:850px){.care-panel{grid-template-columns:1fr!important}.care-panel .care-photo{min-height:150px}}
.topbar{padding:1.3rem 1.55rem!important}.topbar p{max-width:720px!important;font-size:.84rem!important;line-height:1.55!important;color:#42534a!important}.alert-box *,.result-card *,.kcard *,.workspace-note *{opacity:1!important}.alert-box.green{background:#edf7eb!important}.alert-box.orange{background:#fff3df!important}.alert-box.red{background:#fdeceb!important}.alert-box,.alert-box *{color:#183328!important}.result-card,.result-card *{color:#183328!important}.stAlert,.stAlert *{color:#183328!important}.stTextInput label p,.stNumberInput label p,.stSelectbox label p,.stTextArea label p,.stCheckbox label p{color:#19392b!important;font-size:.82rem!important}.composition{display:grid;grid-template-columns:160px 1fr;gap:1rem;padding:1rem 1.2rem;background:#f5f8f1;border-left:4px solid var(--green);margin:.8rem 0}.composition b{font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;color:var(--green)}.composition p{margin:0;max-width:760px;color:#42534a;line-height:1.55;font-size:.82rem}@media(max-width:700px){.composition,.workspace-note{grid-template-columns:1fr;display:grid}}
.workspace-note b{color:#174b2d!important;opacity:1!important;font-weight:700!important}.workspace-note span{color:#40514c!important;opacity:1!important}
.cross-app-link{position:fixed;top:1rem;right:1.7rem;z-index:9999;display:inline-flex;align-items:center;justify-content:center;padding:.62rem 1rem;background:#11131a;color:#fff!important;border:1px solid rgba(255,255,255,.18);border-radius:5px;font:650 .78rem "Stack Sans Text","Segoe UI",sans-serif;text-decoration:none!important;box-shadow:0 3px 12px rgba(0,0,0,.18)}.cross-app-link:hover{filter:brightness(1.12)}</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    flow = pd.read_csv(BASE_DIR / "patient_flow_analyzed.csv", parse_dates=["date"])
    inv  = pd.read_csv(BASE_DIR / "inventory_analyzed.csv", parse_dates=["expiry_date"])
    beds = pd.read_csv(BASE_DIR / "bed_occupancy.csv")
    return flow, inv, beds

@st.cache_data(show_spinner=False)
def load_image_b64(filename):
    image_path = Path(__file__).parent / "assets" / filename
    return base64.b64encode(image_path.read_bytes()).decode("ascii")

flow, inv, beds = load_data()

hero_b64 = load_image_b64("hospital-wellness-hero.webp")
care_b64 = load_image_b64("patient-centred-care.webp")

# Session state
if "admissions" not in st.session_state: st.session_state.admissions = []
if "alerts_log" not in st.session_state: st.session_state.alerts_log = []

def kcard(color, val, lbl, sub=""):
    return f'<div class="kcard {color}"><div class="kval">{val}</div><div class="klbl">{lbl}</div>{"<div class=ksub>"+sub+"</div>" if sub else ""}</div>'

# ── WELLNESS HEADER + NAVIGATION ──────────────────────────────────
available_beds = beds["available_beds"].sum()
expiring_items = (inv["expiring_soon"]==1).sum()
pending_adm    = len(st.session_state.admissions)

st.markdown(f"""
<div class="brandbar">
  <div class="brand"><div class="leafmark"><i></i><i></i></div><div><strong>BGH <span>Wellness</span></strong><small>Botswana General Hospital</small></div></div>
  <div class="brandmeta">Care teams · Hospital operations</div>
</div>
<div class="health-hero" style="background-image:linear-gradient(90deg,rgba(251,248,241,.98) 0%,rgba(251,248,241,.93) 34%,rgba(251,248,241,.12) 64%),url('data:image/webp;base64,{hero_b64}')">
  <div class="hero-copy">
    <div class="eyebrow">Your patients. Our priority.</div>
    <h1>Better Care,<br>Every Shift</h1>
    <p>Give hospital teams a clear view of beds, admissions, essential supplies and patient flow: when every minute matters.</p>
    <a class="hero-cta" href="#health-workspace">Open operations workspace</a>
  </div>
</div>
<div class="care-panel">
  <div class="care-copy"><div class="eyebrow">PATIENT CENTRED OPERATIONS</div><h2>Care Teams Need Clarity</h2><p>BGH Wellness brings ward capacity, admissions, essential inventory and daily patient flow into one dependable workspace: so staff can spend less time searching and more time caring.</p></div>
  <div class="care-photo" style="background-image:url('data:image/webp;base64,{care_b64}')"></div>
</div>
<div class="nav-label">Hospital services</div>
""", unsafe_allow_html=True)

st.markdown('<div id="health-workspace" class="workspace-anchor"></div><div class="workspace-note"><b>Care operations workspace</b><span>Assign beds, process admissions and resolve supply alerts here. Use the separate dashboard for hospital-wide analysis.</span></div>', unsafe_allow_html=True)
nav = st.radio("Hospital services", [
    "Bed availability",
    "Patient admission",
    "Inventory alerts",
    "Patient flow",
    "Admission queue",
], horizontal=True, label_visibility="collapsed")

# ════════════════════════════════════════════════════════════════
# PAGE 1 - BED AVAILABILITY (Real-time bed tracker)
# ════════════════════════════════════════════════════════════════
if nav == "Bed availability":
    st.markdown('<div class="topbar"><h1>Real-Time Bed Availability</h1><p>A clear, hospital-wide view of beds ready for incoming patients.</p></div>', unsafe_allow_html=True)

    total_beds = beds["total_beds"].sum()
    occupied   = beds["occupied_beds"].sum()
    available  = beds["available_beds"].sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kcard("blue",   f"{total_beds}",  "Total Beds",      "Hospital-wide"), unsafe_allow_html=True)
    c2.markdown(kcard("orange", f"{occupied}",    "Currently Full",  f"{occupied/total_beds*100:.0f}% occupancy"), unsafe_allow_html=True)
    c3.markdown(kcard("green",  f"{available}",   "Available NOW",   "Ready for admission"), unsafe_allow_html=True)
    c4.markdown(kcard("red" if available<10 else "green", f"{(beds['occupancy_pct']>90).sum()}","Wards at Capacity","Over 90% full"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Find a Bed")
    st.markdown("**For urgent placement: wards with beds available now.**")
    b1, b2 = st.columns([1.4, 1])
    with b1:
        ward_search = st.text_input("Find a ward", placeholder="Ward name", key="ward_search")
    with b2:
        bed_state = st.selectbox("Bed state", ["All wards", "Available now", "At capacity"])
    visible_beds = beds.copy()
    if ward_search:
        visible_beds = visible_beds[visible_beds["ward_name"].str.contains(ward_search, case=False, na=False)]
    if bed_state == "Available now":
        visible_beds = visible_beds[visible_beds["available_beds"] > 0]
    elif bed_state == "At capacity":
        visible_beds = visible_beds[visible_beds["available_beds"] == 0]
    st.markdown(f'<div class="data-hint">Showing {len(visible_beds)} wards. Availability is based on the current bed-status data.</div>', unsafe_allow_html=True)
    if visible_beds.empty:
        st.info("No wards match the selected filters.")
    for _, ward in visible_beds.iterrows():
        if ward["available_beds"] > 0:
            status_color = "green" if ward["occupancy_pct"] < 75 else "orange"
            icon = "AVAILABLE" if ward["occupancy_pct"] < 75 else "LIMITED"
            st.markdown(f"""
            <div class="alert-box {status_color}">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <b>{icon} {ward['ward_name']}</b><br>
                        <span style="font-size:.85rem">{ward['available_beds']} beds available | {ward['occupancy_pct']:.0f}% full</span>
                    </div>
                    <div style="font-size:1.5rem;font-weight:700">{ward['available_beds']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-box red">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <b>FULL · {ward['ward_name']}</b><br>
                        <span style="font-size:.85rem">FULL: {ward['occupied_beds']}/{ward['total_beds']} beds occupied</span>
                    </div>
                    <div style="font-size:1.5rem;font-weight:700">0</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Bed Turnover Forecast")
    st.caption("Estimated beds that will become available in next 24 hours based on average length of stay")
    turnover = beds[["ward_name","daily_turnover_rate"]].copy()
    turnover["daily_turnover_rate"] = turnover["daily_turnover_rate"].apply(lambda x: f"~{x:.1f} beds")
    turnover.columns = ["Ward","Expected to Free in 24hrs"]
    st.dataframe(turnover.reset_index(drop=True), use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE 2 - PATIENT ADMISSION (Quick admission form)
# ════════════════════════════════════════════════════════════════
elif nav == "Patient admission":
    st.markdown('<div class="topbar"><h1>Patient Admission</h1><p>Place each patient in the right ward using live bed availability.</p></div>', unsafe_allow_html=True)

    st.markdown("### Patient Information")
    col1,col2,col3 = st.columns(3)

    with col1:
        patient_name = st.text_input("Patient Name")
        patient_id   = st.text_input("ID / Omang Number")
        age          = st.number_input("Age", 0, 120, 35)
        gender       = st.selectbox("Gender", ["Male","Female"])

    with col2:
        admission_type = st.selectbox("Admission Type", ["Emergency","Elective Surgery","Transfer","Maternity","Other"])
        department     = st.selectbox("Department", sorted(flow["department"].unique()))
        urgency        = st.selectbox("Urgency", ["Critical: Immediate","Urgent: Within 1 hour","Standard"])

    with col3:
        diagnosis      = st.text_area("Diagnosis / Reason", height=80)
        admitting_dr   = st.text_input("Admitting Doctor")

    st.markdown("---")

    admission_ready = bool(patient_name.strip() and patient_id.strip())
    if not admission_ready:
        st.caption("Required before placement: patient name and ID / Omang number.")
    if st.button("Check bed availability", disabled=not admission_ready, use_container_width=True):
        if not patient_name or not patient_id:
            st.error("Please fill in at least Patient Name and ID.")
        else:
            # Find ward with beds
            ward_mapping = {
                "Emergency": ["General Ward A","General Ward B"],
                "Surgery": ["Surgery Recovery","General Ward A"],
                "Maternity": ["Maternity"],
                "Pediatrics": ["Pediatrics"],
                "ICU": ["ICU"],
                "Outpatient": ["General Ward A","General Ward B"]
            }
            preferred_wards = ward_mapping.get(department, ["General Ward A","General Ward B"])

            available_ward = None
            available_choices = []
            for ward_name in preferred_wards:
                ward_data = beds[beds["ward_name"]==ward_name]
                if len(ward_data) > 0 and ward_data.iloc[0]["available_beds"] > 0:
                    available_choices.append(ward_data.iloc[0])
            for _, ward_row in beds[beds["available_beds"] > 0].iterrows():
                if ward_row["ward_name"] not in [w["ward_name"] for w in available_choices]:
                    available_choices.append(ward_row)
            if available_choices:
                selected_ward_name = st.selectbox("Select an available ward", [w["ward_name"] for w in available_choices], help="Preferred wards are listed first; alternative wards follow.")
                available_ward = next(w for w in available_choices if w["ward_name"] == selected_ward_name)
            
            if available_ward is not None:
                st.markdown(f"""
                <div class="result-card green">
                    <div style="font-size:2rem;font-weight:800">BED AVAILABLE</div>
                    <div style="margin-top:.5rem;font-size:1.1rem">
                        Ward: <b>{available_ward['ward_name']}</b><br>
                        {available_ward['available_beds']} beds currently available
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Save admission
                st.info(f"Confirming will place {patient_name} in {available_ward['ward_name']} with {urgency.lower()} priority.")
                if st.button("Confirm admission", key="confirm_adm", use_container_width=True):
                    st.session_state.admissions.append({
                        "admission_id": f"ADM-{len(st.session_state.admissions)+1:04d}",
                        "date_time":    datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "patient_name": patient_name,
                        "patient_id":   patient_id,
                        "age":          age,
                        "gender":       gender,
                        "department":   department,
                        "ward":         available_ward['ward_name'],
                        "urgency":      urgency,
                        "diagnosis":    diagnosis,
                        "doctor":       admitting_dr,
                        "status":       "Admitted",
                    })
                    st.success(f"Patient admitted to {available_ward['ward_name']}.")
            else:
                st.markdown(f"""
                <div class="result-card orange">
                    <div style="font-size:2rem;font-weight:800">NO BEDS IN PREFERRED WARDS</div>
                    <div style="margin-top:.5rem;font-size:1.1rem">
                        All {', '.join(preferred_wards)} wards are currently full.<br>
                        Check other wards or contact bed coordinator.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### Available Beds in Other Wards")
                other_wards = beds[~beds["ward_name"].isin(preferred_wards) & (beds["available_beds"]>0)]
                if len(other_wards) > 0:
                    for _, w in other_wards.iterrows():
                        st.markdown(f"**{w['ward_name']}**: {w['available_beds']} beds available")
                else:
                    st.error("No beds are available in any ward. Contact hospital administration.")

# ════════════════════════════════════════════════════════════════
# PAGE 3 - INVENTORY ALERTS (Daily medication checks)
# ════════════════════════════════════════════════════════════════
elif nav == "Inventory alerts":
    st.markdown('<div class="topbar"><h1>Medicine & Supply Alerts</h1><p>Protect continuity of care by reviewing expiring and low-stock essentials.</p></div>', unsafe_allow_html=True)

    total_items    = len(inv)
    expiring_count = (inv["expiring_soon"]==1).sum()
    low_stock      = (inv["low_stock"]==1).sum()
    waste_value    = inv["value_at_risk_bwp"].sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kcard("blue",   f"{total_items}",     "Total Items",         "In inventory"), unsafe_allow_html=True)
    c2.markdown(kcard("red",    f"{expiring_count}",  "Expiring Within 30d", "Urgent action"), unsafe_allow_html=True)
    c3.markdown(kcard("orange", f"{low_stock}",       "Low Stock",           "Need to reorder"), unsafe_allow_html=True)
    c4.markdown(kcard("red",    f"P{waste_value:,.0f}","Value at Risk",      "If expire"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Urgent: Expiring Within 30 Days")
    expiring = inv[inv["expiring_soon"]==1].sort_values("days_until_expiry")
    if len(expiring) > 0:
        for _, item in expiring.iterrows():
            days_left = item["days_until_expiry"]
            color = "red" if days_left <= 15 else "orange"
            icon  = "CRITICAL" if days_left <= 15 else "REVIEW"
            st.markdown(f"""
            <div class="alert-box {color}">
                <div style="display:flex;justify-content:space-between;">
                    <div>
                        <b>{icon} {item['item_name']}</b><br>
                        <span style="font-size:.85rem">{days_left} days until expiry | {item['stock_quantity']} units in stock | Value: P{item['value_at_risk_bwp']:,.2f}</span>
                    </div>
                </div>
                <div style="margin-top:.5rem;font-size:.8rem">
                    <b>Action:</b> Use in high-demand departments immediately or redistribute to clinics
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Log alert action
        if st.button("Mark alerts as reviewed"):
            st.session_state.alerts_log.append({
                "date":       str(date.today()),
                "alert_type": "Expiring Medications",
                "items":      expiring_count,
                "reviewed_by":"Pharmacy Staff",
                "action":     "Redistributed to high-usage departments"
            })
            st.success("Review recorded.")
    else:
        st.success("No items are expiring within 30 days.")

    st.markdown("---")
    st.markdown("### Low Stock Alerts")
    low_stock_items = inv[inv["low_stock"]==1].sort_values("days_until_stockout")
    if len(low_stock_items) > 0:
        for _, item in low_stock_items.iterrows():
            st.markdown(f"""
            <div class="alert-box orange">
                <div style="display:flex;justify-content:space-between;">
                    <div>
                        <b>REORDER · {item['item_name']}</b><br>
                        <span style="font-size:.85rem">{item['days_until_stockout']} days until stockout | {item['stock_quantity']} units remaining</span>
                    </div>
                </div>
                <div style="margin-top:.5rem;font-size:.8rem">
                    <b>Action:</b> Place reorder with supplier immediately
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("All monitored items are adequately stocked.")

# ════════════════════════════════════════════════════════════════
# PAGE 4: TODAY'S PATIENT FLOW
# ════════════════════════════════════════════════════════════════
elif nav == "Patient flow":
    st.markdown('<div class="topbar"><h1>Today\'s Patient Flow</h1><p>Current shift activity, pressure points and patient wait times.</p></div>', unsafe_allow_html=True)

    # Simulate "today" as most recent date in data
    today_data = flow[flow["date"] == flow["date"].max()]

    current_patients = today_data["patients_arrived"].sum()
    current_wait     = today_data["wait_time_min"].mean()
    staff_on_duty    = today_data["staff_on_duty"].sum()

    c1,c2,c3 = st.columns(3)
    c1.markdown(kcard("blue",   f"{current_patients}",     "Patients Today",      "All departments"), unsafe_allow_html=True)
    c2.markdown(kcard("orange", f"{current_wait:.0f} min", "Current Avg Wait",    "Across shifts"), unsafe_allow_html=True)
    c3.markdown(kcard("blue",   f"{staff_on_duty}",        "Total Staff on Duty", "Hospital-wide"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Department Status: Current Shift")
    dept_today = today_data.groupby("department").agg(
        patients=("patients_arrived","sum"),
        wait=("wait_time_min","mean"),
        staff=("staff_on_duty","sum")
    ).reset_index()
    dept_today = dept_today.sort_values("wait", ascending=False)

    for _, dept in dept_today.iterrows():
        wait_val = dept["wait"]
        color = "red" if wait_val > 45 else "orange" if wait_val > 30 else "green"
        icon  = "HIGH" if wait_val > 45 else "WATCH" if wait_val > 30 else "ON TRACK"
        st.markdown(f"""
        <div class="alert-box {color}">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <b>{icon} {dept['department']}</b><br>
                    <span style="font-size:.85rem">{dept['patients']:.0f} patients | {dept['staff']:.0f} staff on duty</span>
                </div>
                <div style="font-size:1.2rem;font-weight:700">{wait_val:.0f} min wait</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE 5 - ADMISSION QUEUE
# ════════════════════════════════════════════════════════════════
elif nav == "Admission queue":
    st.markdown(f'<div class="topbar"><h1>Admission Queue</h1><p>Every patient admission processed during the current shift. Last reviewed {datetime.now():%d %b %Y, %H:%M}.</p></div>', unsafe_allow_html=True)

    adm = st.session_state.admissions
    c1,c2,c3 = st.columns(3)
    c1.markdown(kcard("blue",   f"{len(adm)}",                           "Total Admissions",    "Today"), unsafe_allow_html=True)
    c2.markdown(kcard("green",  f"{len([a for a in adm if a['status']=='Admitted'])}", "Currently Admitted", "In wards"), unsafe_allow_html=True)
    c3.markdown(kcard("orange", f"{len([a for a in adm if 'Critical' in a['urgency']])}", "Critical Cases",     "Urgent priority"), unsafe_allow_html=True)

    st.markdown("---")
    if not adm:
        st.info("No admissions logged yet today. Use **Patient Admission** to add patients.")
    else:
        q1, q2 = st.columns([1.4, 1])
        with q1:
            patient_search = st.text_input("Find a patient", placeholder="Patient name or admission ID", key="admission_search")
        with q2:
            urgency_filter = st.multiselect("Urgency", sorted({a["urgency"] for a in adm}), key="admission_urgency")
        visible_adm = adm
        if patient_search:
            term = patient_search.lower()
            visible_adm = [a for a in visible_adm if term in str(a.get("patient_name", "")).lower() or term in str(a.get("admission_id", "")).lower()]
        if urgency_filter:
            visible_adm = [a for a in visible_adm if a["urgency"] in urgency_filter]
        st.markdown(f'<div class="data-hint">Showing {len(visible_adm)} of {len(adm)} admissions for the current shift.</div>', unsafe_allow_html=True)
        if not visible_adm:
            st.info("No admissions match the current filters.")
        for i, a in enumerate(visible_adm):
            urgency_color = "red" if "Critical" in a["urgency"] else "orange" if "Urgent" in a["urgency"] else "green"
            st.markdown(f"""
            <div class="alert-box {urgency_color}">
                <div style="display:flex;justify-content:space-between;">
                    <div>
                        <b>{a['admission_id']}</b>: {a['patient_name']} ({a['age']}{a['gender'][0]}): {a['department']}<br>
                        <span style="font-size:.85rem">Ward: {a['ward']} | Doctor: {a['doctor']} | {a['date_time']}</span>
                    </div>
                    <div style="font-weight:700">{a['urgency']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            details, controls = st.columns([2, 1])
            with details:
                with st.expander(f"View {a['admission_id']} details"):
                    st.markdown(f"**Patient:** {a['patient_name']}  \n**Patient ID:** {a['patient_id']}  \n**Department:** {a['department']}  \n**Ward:** {a['ward']}  \n**Doctor:** {a['doctor'] or 'Not recorded'}  \n**Reason:** {a['diagnosis'] or 'Not recorded'}  \n**Admitted:** {a['date_time']}")
            with controls:
                states = ["Waiting", "Bed Assigned", "Admitted", "Transferred", "Discharged"]
                current_state = a.get("status", "Admitted")
                if current_state not in states: current_state = "Admitted"
                new_state = st.selectbox("Admission status", states, index=states.index(current_state), key=f"adm_status_{i}")
                if new_state != a.get("status"):
                    a["status"] = new_state
                    a["updated_at"] = datetime.now().strftime("%d %b %Y, %H:%M")
                    st.success(f"{a['admission_id']} moved to {new_state}.")
        
        csv = pd.DataFrame(adm).to_csv(index=False).encode()
        st.download_button("Export admission log", csv, "admissions_today.csv", "text/csv")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#687269;font-size:.74rem'>Botswana General Hospital · Clinical Operations · 2026</div>", unsafe_allow_html=True)
