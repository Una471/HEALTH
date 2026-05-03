"""
Botswana General Hospital — HOSPITAL MANAGEMENT SYSTEM
Daily operational tool for staff. CLEAR TEXT COLORS.
Run: streamlit run 04_software.py --server.port 8502
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Botswana General Hospital | Operations", page_icon="🏥", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#f8f9fa;color:#212529;}
.topbar{background:linear-gradient(135deg,#1976d2,#1565c0);color:white;padding:1.2rem 1.5rem;border-radius:12px;margin-bottom:1.2rem;}
.topbar h1{margin:0;font-size:1.4rem;color:white;}
.topbar p{margin:.2rem 0 0;color:#e3f2fd;opacity:.9;font-size:.82rem;}
.kcard{background:white;border-radius:10px;padding:1.1rem 1.3rem;box-shadow:0 2px 10px rgba(0,0,0,.08);border-top:3px solid #dee2e6;margin-bottom:.3rem;}
.kcard.red{border-top-color:#d32f2f;} .kcard.orange{border-top-color:#f57c00;}
.kcard.green{border-top-color:#388e3c;} .kcard.blue{border-top-color:#1976d2;}
.kval{font-size:1.8rem;font-weight:700;color:#212529;}
.klbl{font-size:.7rem;text-transform:uppercase;letter-spacing:1.5px;color:#6c757d;margin-top:.3rem;}
.ksub{font-size:.76rem;color:#495057;margin-top:.3rem;}
.result-card{border-radius:12px;padding:1.8rem;margin:1rem 0;border:2px solid;text-align:center;}
.result-card.green{background:#e8f5e9;border-color:#388e3c;color:#1b5e20;}
.result-card.orange{background:#fff3e0;border-color:#f57c00;color:#e65100;}
.result-card.red{background:#ffebee;border-color:#d32f2f;color:#b71c1c;}
.alert-box{border-radius:10px;padding:1rem;margin:.5rem 0;border-left:4px solid;}
.alert-box.red{background:#ffebee;border-color:#d32f2f;color:#b71c1c;}
.alert-box.orange{background:#fff3e0;border-color:#f57c00;color:#e65100;}
.alert-box.green{background:#e8f5e9;border-color:#388e3c;color:#1b5e20;}
section[data-testid="stSidebar"]{background:#1565c0!important;}
section[data-testid="stSidebar"] *{color:#e3f2fd!important;}
.stTextInput input,.stNumberInput input,.stSelectbox select,.stTextArea textarea{
    background:white!important;color:#212529!important;border:1px solid #ced4da!important;}
.stButton>button{background:#1976d2;color:white;border:none;border-radius:8px;padding:.6rem 1.5rem;font-weight:600;width:100%;}
.stButton>button:hover{background:#1565c0;}
#MainMenu,footer,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    flow = pd.read_csv("patient_flow_analyzed.csv", parse_dates=["date"])
    inv  = pd.read_csv("inventory_analyzed.csv", parse_dates=["expiry_date"])
    beds = pd.read_csv("bed_occupancy.csv")
    return flow, inv, beds

flow, inv, beds = load_data()

# Session state
if "admissions" not in st.session_state: st.session_state.admissions = []
if "alerts_log" not in st.session_state: st.session_state.alerts_log = []

def kcard(color, val, lbl, sub=""):
    return f'<div class="kcard {color}"><div class="kval">{val}</div><div class="klbl">{lbl}</div>{"<div class=ksub>"+sub+"</div>" if sub else ""}</div>'

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 Hospital Operations")
    st.markdown("*Botswana General Hospital*")
    st.markdown("---")
    nav = st.radio("Go to", [
        "🛏️  Bed Availability",
        "🚨  Patient Admission",
        "💊  Inventory Alerts",
        "📊  Today's Patient Flow",
        "📋  Admission Queue",
    ])
    st.markdown("---")
    available_beds = beds["available_beds"].sum()
    expiring_items = (inv["expiring_soon"]==1).sum()
    pending_adm    = len(st.session_state.admissions)
    st.markdown(f"🛏️ **Available beds:** {available_beds}")
    st.markdown(f"💊 **Expiring items:** {expiring_items}")
    st.markdown(f"📋 **Pending admissions:** {pending_adm}")

# ════════════════════════════════════════════════════════════════
# PAGE 1 — BED AVAILABILITY (Real-time bed tracker)
# ════════════════════════════════════════════════════════════════
if nav == "🛏️  Bed Availability":
    st.markdown('<div class="topbar"><h1>🛏️ Real-Time Bed Availability</h1><p>Instant bed status for emergency admissions</p></div>', unsafe_allow_html=True)

    total_beds = beds["total_beds"].sum()
    occupied   = beds["occupied_beds"].sum()
    available  = beds["available_beds"].sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kcard("blue",   f"{total_beds}",  "Total Beds",      "Hospital-wide"), unsafe_allow_html=True)
    c2.markdown(kcard("orange", f"{occupied}",    "Currently Full",  f"{occupied/total_beds*100:.0f}% occupancy"), unsafe_allow_html=True)
    c3.markdown(kcard("green",  f"{available}",   "Available NOW",   "Ready for admission"), unsafe_allow_html=True)
    c4.markdown(kcard("red" if available<10 else "green", f"{(beds['occupancy_pct']>90).sum()}","Wards at Capacity","Over 90% full"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔍 Quick Bed Finder")
    st.markdown("**Use this for emergency admissions — shows which wards have beds available RIGHT NOW**")

    for _, ward in beds.iterrows():
        if ward["available_beds"] > 0:
            status_color = "green" if ward["occupancy_pct"] < 75 else "orange"
            icon = "🟢" if ward["occupancy_pct"] < 75 else "🟡"
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
                        <b>🔴 {ward['ward_name']}</b><br>
                        <span style="font-size:.85rem">FULL — {ward['occupied_beds']}/{ward['total_beds']} beds occupied</span>
                    </div>
                    <div style="font-size:1.5rem;font-weight:700">0</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Bed Turnover Forecast")
    st.caption("Estimated beds that will become available in next 24 hours based on average length of stay")
    turnover = beds[["ward_name","daily_turnover_rate"]].copy()
    turnover["daily_turnover_rate"] = turnover["daily_turnover_rate"].apply(lambda x: f"~{x:.1f} beds")
    turnover.columns = ["Ward","Expected to Free in 24hrs"]
    st.dataframe(turnover.reset_index(drop=True), use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE 2 — PATIENT ADMISSION (Quick admission form)
# ════════════════════════════════════════════════════════════════
elif nav == "🚨  Patient Admission":
    st.markdown('<div class="topbar"><h1>🚨 Patient Admission</h1><p>Quick admission form with instant bed availability check</p></div>', unsafe_allow_html=True)

    st.markdown("### 👤 Patient Information")
    col1,col2,col3 = st.columns(3)

    with col1:
        patient_name = st.text_input("Patient Name")
        patient_id   = st.text_input("ID / Omang Number")
        age          = st.number_input("Age", 0, 120, 35)
        gender       = st.selectbox("Gender", ["Male","Female"])

    with col2:
        admission_type = st.selectbox("Admission Type", ["Emergency","Elective Surgery","Transfer","Maternity","Other"])
        department     = st.selectbox("Department", sorted(flow["department"].unique()))
        urgency        = st.selectbox("Urgency", ["Critical - Immediate","Urgent - Within 1 hour","Standard"])

    with col3:
        diagnosis      = st.text_area("Diagnosis / Reason", height=80)
        admitting_dr   = st.text_input("Admitting Doctor")

    st.markdown("---")

    if st.button("🔍  CHECK BED AVAILABILITY & ADMIT"):
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
            for ward_name in preferred_wards:
                ward_data = beds[beds["ward_name"]==ward_name]
                if len(ward_data) > 0 and ward_data.iloc[0]["available_beds"] > 0:
                    available_ward = ward_data.iloc[0]
                    break
            
            if available_ward is not None:
                st.markdown(f"""
                <div class="result-card green">
                    <div style="font-size:2.5rem;margin-bottom:.5rem">✅</div>
                    <div style="font-size:2rem;font-weight:800">BED AVAILABLE</div>
                    <div style="margin-top:.5rem;font-size:1.1rem">
                        Ward: <b>{available_ward['ward_name']}</b><br>
                        {available_ward['available_beds']} beds currently available
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Save admission
                if st.button("✅  CONFIRM ADMISSION", key="confirm_adm"):
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
                    st.success(f"✅ Patient admitted to {available_ward['ward_name']}!")
            else:
                st.markdown(f"""
                <div class="result-card orange">
                    <div style="font-size:2.5rem;margin-bottom:.5rem">⚠️</div>
                    <div style="font-size:2rem;font-weight:800">NO BEDS IN PREFERRED WARDS</div>
                    <div style="margin-top:.5rem;font-size:1.1rem">
                        All {', '.join(preferred_wards)} wards are currently full.<br>
                        Check other wards or contact bed coordinator.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### Available Beds in Other Wards:")
                other_wards = beds[~beds["ward_name"].isin(preferred_wards) & (beds["available_beds"]>0)]
                if len(other_wards) > 0:
                    for _, w in other_wards.iterrows():
                        st.markdown(f"🟢 **{w['ward_name']}** — {w['available_beds']} beds available")
                else:
                    st.error("🔴 No beds available in any ward. Contact hospital administration.")

# ════════════════════════════════════════════════════════════════
# PAGE 3 — INVENTORY ALERTS (Daily medication checks)
# ════════════════════════════════════════════════════════════════
elif nav == "💊  Inventory Alerts":
    st.markdown('<div class="topbar"><h1>💊 Inventory Alerts</h1><p>Medications expiring soon or running low on stock</p></div>', unsafe_allow_html=True)

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
    st.markdown("### 🔴 URGENT — Expiring Within 30 Days")
    expiring = inv[inv["expiring_soon"]==1].sort_values("days_until_expiry")
    if len(expiring) > 0:
        for _, item in expiring.iterrows():
            days_left = item["days_until_expiry"]
            color = "red" if days_left <= 15 else "orange"
            icon  = "🔴" if days_left <= 15 else "🟠"
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
        if st.button("📋  Log Alert Reviewed"):
            st.session_state.alerts_log.append({
                "date":       str(date.today()),
                "alert_type": "Expiring Medications",
                "items":      expiring_count,
                "reviewed_by":"Pharmacy Staff",
                "action":     "Redistributed to high-usage departments"
            })
            st.success("✅ Alert logged!")
    else:
        st.success("✅ No items expiring within 30 days")

    st.markdown("---")
    st.markdown("### 🟠 Low Stock Alerts")
    low_stock_items = inv[inv["low_stock"]==1].sort_values("days_until_stockout")
    if len(low_stock_items) > 0:
        for _, item in low_stock_items.iterrows():
            st.markdown(f"""
            <div class="alert-box orange">
                <div style="display:flex;justify-content:space-between;">
                    <div>
                        <b>🟠 {item['item_name']}</b><br>
                        <span style="font-size:.85rem">{item['days_until_stockout']} days until stockout | {item['stock_quantity']} units remaining</span>
                    </div>
                </div>
                <div style="margin-top:.5rem;font-size:.8rem">
                    <b>Action:</b> Place reorder with supplier immediately
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ All items adequately stocked")

# ════════════════════════════════════════════════════════════════
# PAGE 4 — TODAY'S PATIENT FLOW
# ════════════════════════════════════════════════════════════════
elif nav == "📊  Today's Patient Flow":
    st.markdown('<div class="topbar"><h1>📊 Today\'s Patient Flow</h1><p>Current shift activity and wait times</p></div>', unsafe_allow_html=True)

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
    st.markdown("### 📋 Department Status — Current Shift")
    dept_today = today_data.groupby("department").agg(
        patients=("patients_arrived","sum"),
        wait=("wait_time_min","mean"),
        staff=("staff_on_duty","sum")
    ).reset_index()
    dept_today = dept_today.sort_values("wait", ascending=False)
    
    for _, dept in dept_today.iterrows():
        wait_val = dept["wait"]
        color = "red" if wait_val > 45 else "orange" if wait_val > 30 else "green"
        icon  = "🔴" if wait_val > 45 else "🟠" if wait_val > 30 else "🟢"
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
# PAGE 5 — ADMISSION QUEUE
# ════════════════════════════════════════════════════════════════
elif nav == "📋  Admission Queue":
    st.markdown('<div class="topbar"><h1>📋 Admission Queue</h1><p>All patient admissions processed today</p></div>', unsafe_allow_html=True)

    adm = st.session_state.admissions
    c1,c2,c3 = st.columns(3)
    c1.markdown(kcard("blue",   f"{len(adm)}",                           "Total Admissions",    "Today"), unsafe_allow_html=True)
    c2.markdown(kcard("green",  f"{len([a for a in adm if a['status']=='Admitted'])}", "Currently Admitted", "In wards"), unsafe_allow_html=True)
    c3.markdown(kcard("orange", f"{len([a for a in adm if 'Critical' in a['urgency']])}", "Critical Cases",     "Urgent priority"), unsafe_allow_html=True)

    st.markdown("---")
    if not adm:
        st.info("No admissions logged yet today. Use **Patient Admission** to add patients.")
    else:
        for i, a in enumerate(adm):
            urgency_color = "red" if "Critical" in a["urgency"] else "orange" if "Urgent" in a["urgency"] else "green"
            st.markdown(f"""
            <div class="alert-box {urgency_color}">
                <div style="display:flex;justify-content:space-between;">
                    <div>
                        <b>{a['admission_id']}</b> — {a['patient_name']} ({a['age']}{a['gender'][0]}) — {a['department']}<br>
                        <span style="font-size:.85rem">Ward: {a['ward']} | Doctor: {a['doctor']} | {a['date_time']}</span>
                    </div>
                    <div style="font-weight:700">{a['urgency']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        csv = pd.DataFrame(adm).to_csv(index=False).encode()
        st.download_button("📥 Export Admission Log", csv, "admissions_today.csv", "text/csv")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#6c757d;font-size:.78rem'>Botswana General Hospital · Operations System · Unaswi Leonard · 2026</div>", unsafe_allow_html=True)
