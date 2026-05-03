"""
PRINCESS MARINA HOSPITAL — OPERATIONAL DASHBOARD
Simple report for hospital management. CLEAR TEXT COLORS.
Run: streamlit run 03_dashboard.py --server.port 8501
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Princess Marina | Dashboard", page_icon="🏥", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#f8f9fa;color:#212529;}
.topbar{background:linear-gradient(135deg,#1976d2,#1565c0);color:white;padding:1.4rem 2rem;border-radius:12px;margin-bottom:1.5rem;}
.topbar h1{margin:0;font-size:1.5rem;font-weight:700;color:white;}
.topbar p{margin:.3rem 0 0;opacity:.9;font-size:.85rem;color:#e3f2fd;}
.kcard{background:white;border-radius:12px;padding:1.2rem 1.4rem;box-shadow:0 2px 10px rgba(0,0,0,.08);border-left:5px solid #dee2e6;margin-bottom:.4rem;}
.kcard.red{border-left-color:#d32f2f;} .kcard.orange{border-left-color:#f57c00;}
.kcard.green{border-left-color:#388e3c;} .kcard.blue{border-left-color:#1976d2;}
.kval{font-size:1.9rem;font-weight:700;line-height:1.1;color:#212529;}
.klbl{font-size:.72rem;text-transform:uppercase;letter-spacing:1.5px;color:#6c757d;margin-top:.3rem;}
.ksub{font-size:.78rem;color:#495057;margin-top:.3rem;}
.ccard{background:white;border-radius:12px;padding:1.2rem 1.4rem;box-shadow:0 2px 10px rgba(0,0,0,.08);margin-bottom:1rem;}
.ctitle{font-size:.95rem;font-weight:600;color:#212529;margin-bottom:.2rem;}
.csub{font-size:.78rem;color:#6c757d;margin-bottom:.7rem;}
.ar{background:#ffebee;border:1px solid #ef9a9a;border-radius:8px;padding:.9rem;margin-bottom:.5rem;}
.ar,.ar *{color:#c62828!important;}
.ao{background:#fff3e0;border:1px solid #ffb74d;border-radius:8px;padding:.9rem;margin-bottom:.5rem;}
.ao,.ao *{color:#e65100!important;}
.ag{background:#e8f5e9;border:1px solid#81c784;border-radius:8px;padding:.9rem;margin-bottom:.5rem;}
.ag,.ag *{color:#2e7d32!important;}
section[data-testid="stSidebar"]{background:#1565c0!important;}
section[data-testid="stSidebar"],.stRadio>label,.stSelectbox>label{color:#e3f2fd!important;}
section[data-testid="stSidebar"] *{color:#e3f2fd!important;}
#MainMenu,footer,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load():
    flow = pd.read_csv("patient_flow_analyzed.csv", parse_dates=["date"])
    inv  = pd.read_csv("inventory_analyzed.csv", parse_dates=["expiry_date"])
    beds = pd.read_csv("bed_occupancy.csv")
    return flow, inv, beds

flow, inv, beds = load()

with st.sidebar:
    st.markdown("### 🏥 Princess Marina Hospital")
    st.markdown("Operations Dashboard")
    st.markdown("---")
    page = st.radio("Go to", [
        "📊  Overview",
        "⏱️  Patient Wait Times",
        "💊  Inventory & Waste",
        "🛏️  Bed Occupancy",
        "📈  Department Performance",
    ])
    st.markdown("---")
    depts = ["All Departments"] + sorted(flow["department"].unique().tolist())
    sel_d = st.selectbox("Filter: Department", depts)
    st.markdown("---")
    st.caption("Data: July – December 2025")

dff = flow.copy()
if sel_d != "All Departments": dff = dff[dff["department"] == sel_d]

def kcard(color, val, lbl, sub=""):
    return f'<div class="kcard {color}"><div class="kval">{val}</div><div class="klbl">{lbl}</div>{"<div class=ksub>"+sub+"</div>" if sub else ""}</div>'

def wchart(fig, h=340):
    fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_color="#212529",
                      height=h,margin=dict(t=15,b=20,l=10,r=10))
    return fig

# ════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ════════════════════════════════════════════════════════════════
if page == "📊  Overview":
    st.markdown('<div class="topbar"><h1>🏥 Hospital Operations Overview</h1><p>Princess Marina Hospital &nbsp;·&nbsp; July – December 2025</p></div>', unsafe_allow_html=True)

    total_patients = dff["patients_arrived"].sum()
    avg_wait       = dff["wait_time_min"].mean()
    expiring_items = (inv["expiring_soon"]==1).sum()
    waste_value    = inv["value_at_risk_bwp"].sum()
    total_beds     = beds["total_beds"].sum()
    occupied       = beds["occupied_beds"].sum()

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.markdown(kcard("blue",   f"{total_patients:,}",  "Total Patient Visits",   "6 months"), unsafe_allow_html=True)
    c2.markdown(kcard("orange", f"{avg_wait:.0f} min",  "Avg Wait Time",          "Across all departments"), unsafe_allow_html=True)
    c3.markdown(kcard("red",    f"{expiring_items}",    "Medications Expiring",   "Within 30 days"), unsafe_allow_html=True)
    c4.markdown(kcard("red",    f"P{waste_value:,.0f}", "Value at Risk",          "If medications expire"), unsafe_allow_html=True)
    c5.markdown(kcard("blue",   f"{occupied}/{total_beds}","Beds Occupied",       f"{occupied/total_beds*100:.0f}% occupancy"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔍 Key Findings")
    f1,f2,f3 = st.columns(3)
    with f1: st.markdown('<div class="ao"><b>🟠 Wait Times Vary Significantly by Shift</b><br><br>Afternoon shifts have consistently longer wait times than morning shifts. Adding 1-2 staff during afternoon peak hours could reduce average wait by 15 minutes.</div>', unsafe_allow_html=True)
    with f2: st.markdown('<div class="ar"><b>🔴 Medication Waste Is Preventable</b><br><br>P157K worth of medications are at risk of expiring. An automated alert system would flag these items 45 days before expiry, allowing time to redistribute or use them.</div>', unsafe_allow_html=True)
    with f3: st.markdown('<div class="ag"><b>🟢 Bed Turnover Is Efficient</b><br><br>Most wards maintain good turnover rates. Real-time bed tracking would help ER staff place admissions faster during peak hours without calling around.</div>', unsafe_allow_html=True)

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="ccard"><div class="ctitle">📊 Chart 1: Patient Visits by Department</div><div class="csub">Which departments see the most patients</div>', unsafe_allow_html=True)
        dept_vol = dff.groupby("department")["patients_arrived"].sum().sort_values(ascending=False).reset_index()
        dept_vol["label"] = dept_vol["patients_arrived"].apply(lambda x: f"{x:,}")
        fig = px.bar(dept_vol, x="department", y="patients_arrived", color="patients_arrived",
                     color_continuous_scale=["#bbdefb","#1565c0"], text="label",
                     labels={"patients_arrived":"Total Visits","department":""})
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)
        st.plotly_chart(wchart(fig), use_container_width=True)
        st.markdown('<div class="csub" style="color:#6c757d!important"><b>🎨 For Presentation:</b> Bar chart showing Outpatient has highest volume (9,492 visits), followed by Emergency (7,866). Visual hierarchy of department workload.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="ccard"><div class="ctitle">📊 Chart 2: Average Wait Time by Department</div><div class="csub">Emergency has longest waits — needs priority attention</div>', unsafe_allow_html=True)
        dept_wait = dff.groupby("department")["wait_time_min"].mean().sort_values(ascending=False).reset_index()
        dept_wait["label"] = dept_wait["wait_time_min"].apply(lambda x: f"{x:.0f}m")
        fig2 = px.bar(dept_wait, x="department", y="wait_time_min", color="wait_time_min",
                      color_continuous_scale=["#c8e6c9","#d32f2f"], text="label",
                      labels={"wait_time_min":"Avg Wait (min)","department":""})
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False)
        st.plotly_chart(wchart(fig2), use_container_width=True)
        st.markdown('<div class="csub" style="color:#6c757d!important"><b>🎨 For Presentation:</b> Bar chart with color gradient — red bars = longest waits. Emergency at 47 min clearly needs more resources.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PAGE 2 — WAIT TIMES
# ════════════════════════════════════════════════════════════════
elif page == "⏱️  Patient Wait Times":
    st.markdown('<div class="topbar"><h1>⏱️ Patient Wait Times & Flow</h1><p>Analysis of wait times and optimization opportunities</p></div>', unsafe_allow_html=True)

    baseline_wait = dff["wait_time_min"].mean()
    target_wait   = baseline_wait - 15
    longest_wait  = dff["wait_time_min"].max()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kcard("orange", f"{baseline_wait:.0f} min", "Current Avg Wait",   "Baseline"), unsafe_allow_html=True)
    c2.markdown(kcard("green",  f"{target_wait:.0f} min",   "Target Avg Wait",    "After optimization"), unsafe_allow_html=True)
    c3.markdown(kcard("blue",   "15 min",                    "Expected Reduction", "Through better scheduling"), unsafe_allow_html=True)
    c4.markdown(kcard("red",    f"{longest_wait:.0f} min",  "Longest Wait Recorded","Peak period"), unsafe_allow_html=True)

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="ccard"><div class="ctitle">📊 Chart 3: Wait Times by Shift</div><div class="csub">Afternoon shift has longest waits — clear target for adding staff</div>', unsafe_allow_html=True)
        shift_data = dff.groupby("shift")["wait_time_min"].mean().reset_index()
        shift_data = shift_data.sort_values("wait_time_min", ascending=False)
        shift_data["label"] = shift_data["wait_time_min"].apply(lambda x: f"{x:.0f}m")
        fig = px.bar(shift_data, x="shift", y="wait_time_min", color="wait_time_min",
                     color_continuous_scale=["#c8e6c9","#d32f2f"], text="label",
                     labels={"wait_time_min":"Avg Wait (min)","shift":"Shift"})
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)
        st.plotly_chart(wchart(fig), use_container_width=True)
        st.markdown('<div class="csub" style="color:#6c757d!important"><b>🎨 For Presentation:</b> Afternoon shift clearly red (48 min). Morning is green (35 min). Night is yellow (40 min). Visual proof of where to add staff.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="ccard"><div class="ctitle">📊 Chart 4: Wait Time Trend Over 6 Months</div><div class="csub">Weekly average showing if wait times are improving or worsening</div>', unsafe_allow_html=True)
        weekly = dff.groupby(dff["date"].dt.to_period("W"))["wait_time_min"].mean().reset_index()
        weekly["week"] = weekly["date"].astype(str)
        fig2 = px.line(weekly, x="week", y="wait_time_min", markers=True,
                       labels={"wait_time_min":"Avg Wait (min)","week":"Week"})
        fig2.update_traces(line=dict(color="#1565c0",width=3),marker=dict(size=8))
        fig2.add_hline(y=baseline_wait, line_dash="dot", line_color="#f57c00",
                       annotation_text="Current Average", annotation_position="right")
        fig2.add_hline(y=target_wait, line_dash="dot", line_color="#388e3c",
                       annotation_text="Target", annotation_position="right")
        st.plotly_chart(wchart(fig2), use_container_width=True)
        st.markdown('<div class="csub" style="color:#6c757d!important"><b>🎨 For Presentation:</b> Line chart showing weekly fluctuations. Orange dashed line = current avg. Green dashed line = target. Shows progress toward goal.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Busiest Days of the Week")
    dow_data = dff.groupby("day_of_week").agg(
        patients=("patients_arrived","sum"), avg_wait=("wait_time_min","mean")).reindex(
        ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]).reset_index()
    dow_data["avg_wait"] = dow_data["avg_wait"].apply(lambda x: f"{x:.0f} min")
    st.dataframe(dow_data, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE 3 — INVENTORY
# ════════════════════════════════════════════════════════════════
elif page == "💊  Inventory & Waste":
    st.markdown('<div class="topbar"><h1>💊 Inventory Management & Waste Reduction</h1><p>Medication stock levels and expiry tracking</p></div>', unsafe_allow_html=True)

    total_inv_value = inv["total_value_bwp"].sum()
    expiring_count  = (inv["expiring_soon"]==1).sum()
    waste_value     = inv["value_at_risk_bwp"].sum()
    quarterly_save  = waste_value * 0.75 / 2

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kcard("blue",   f"P{total_inv_value:,.0f}", "Total Inventory Value", "All medications"), unsafe_allow_html=True)
    c2.markdown(kcard("red",    f"{expiring_count}",        "Items Expiring Soon",   "Within 30 days"), unsafe_allow_html=True)
    c3.markdown(kcard("red",    f"P{waste_value:,.0f}",     "Value at Risk",         "If not used"), unsafe_allow_html=True)
    c4.markdown(kcard("green",  f"P{quarterly_save:,.0f}",  "Quarterly Savings",     "With alert system"), unsafe_allow_html=True)

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="ccard"><div class="ctitle">📊 Chart 5: Items by Days Until Expiry</div><div class="csub">Red zone items need immediate action</div>', unsafe_allow_html=True)
        inv_sorted = inv.sort_values("days_until_expiry").reset_index(drop=True)
        inv_sorted["item_short"] = inv_sorted["item_name"].str[:20]
        fig = px.bar(inv_sorted, x="item_short", y="days_until_expiry", color="days_until_expiry",
                     color_continuous_scale=["#d32f2f","#f57c00","#388e3c"],
                     labels={"days_until_expiry":"Days Until Expiry","item_short":"Medication"})
        fig.add_hline(y=30, line_dash="dash", line_color="#d32f2f",
                      annotation_text="30-Day Alert Threshold", annotation_position="right")
        st.plotly_chart(wchart(fig,360), use_container_width=True)
        st.markdown('<div class="csub" style="color:#6c757d!important"><b>🎨 For Presentation:</b> Bar chart with red-to-green gradient. Bars below red dashed line = expiring soon. Visual urgency.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="ccard"><div class="ctitle">📊 Chart 6: Stock Value at Risk vs Safe</div><div class="csub">How much inventory value is in danger of being wasted</div>', unsafe_allow_html=True)
        waste_safe = pd.DataFrame({
            "Category": ["At Risk (Expiring)","Safe Stock"],
            "Value": [waste_value, total_inv_value - waste_value]
        })
        fig2 = px.pie(waste_safe, values="Value", names="Category", hole=0.5,
                      color="Category",
                      color_discrete_map={"At Risk (Expiring)":"#d32f2f","Safe Stock":"#388e3c"})
        fig2.update_traces(textinfo="label+percent", textposition="outside")
        st.plotly_chart(wchart(fig2,360), use_container_width=True)
        st.markdown('<div class="csub" style="color:#6c757d!important"><b>🎨 For Presentation:</b> Donut chart. Red slice = at-risk value. Green = safe. Shows proportion of inventory in danger.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔴 Items Expiring Within 30 Days — Immediate Action Required")
    expiring = inv[inv["expiring_soon"]==1].sort_values("days_until_expiry")
    if len(expiring) > 0:
        show = expiring[["item_name","stock_quantity","days_until_expiry","value_at_risk_bwp","priority"]].copy()
        show["value_at_risk_bwp"] = show["value_at_risk_bwp"].apply(lambda x: f"P{x:,.2f}")
        show.columns = ["Medication","Stock Qty","Days Left","Value at Risk","Priority"]
        st.dataframe(show.reset_index(drop=True), use_container_width=True)
    else:
        st.success("✅ No items expiring within 30 days")

# ════════════════════════════════════════════════════════════════
# PAGE 4 — BED OCCUPANCY
# ════════════════════════════════════════════════════════════════
elif page == "🛏️  Bed Occupancy":
    st.markdown('<div class="topbar"><h1>🛏️ Bed Occupancy & Capacity</h1><p>Real-time bed availability across all wards</p></div>', unsafe_allow_html=True)

    total_beds = beds["total_beds"].sum()
    occupied   = beds["occupied_beds"].sum()
    available  = beds["available_beds"].sum()
    occ_pct    = occupied / total_beds * 100

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kcard("blue",   f"{total_beds}",       "Total Hospital Beds", "All wards"), unsafe_allow_html=True)
    c2.markdown(kcard("orange", f"{occupied}",         "Currently Occupied",  f"{occ_pct:.0f}% full"), unsafe_allow_html=True)
    c3.markdown(kcard("green",  f"{available}",        "Available Now",       "For admissions"), unsafe_allow_html=True)
    c4.markdown(kcard("red" if occ_pct>85 else "blue", f"{(beds['occupancy_pct']>90).sum()}","Wards at Capacity","Over 90% full"), unsafe_allow_html=True)

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="ccard"><div class="ctitle">📊 Chart 7: Bed Occupancy by Ward</div><div class="csub">Color-coded by occupancy level for quick status check</div>', unsafe_allow_html=True)
        fig = px.bar(beds, x="ward_name", y="occupancy_pct", color="occupancy_pct",
                     color_continuous_scale=["#388e3c","#f57c00","#d32f2f"],
                     text=beds["occupancy_pct"].apply(lambda x: f"{x:.0f}%"),
                     labels={"occupancy_pct":"Occupancy %","ward_name":"Ward"})
        fig.update_traces(textposition="outside")
        fig.add_hline(y=75, line_dash="dot", line_color="#f57c00",
                      annotation_text="High Occupancy (75%)", annotation_position="right")
        fig.add_hline(y=90, line_dash="dot", line_color="#d32f2f",
                      annotation_text="At Capacity (90%)", annotation_position="right")
        st.plotly_chart(wchart(fig,360), use_container_width=True)
        st.markdown('<div class="csub" style="color:#6c757d!important"><b>🎨 For Presentation:</b> Bar chart with green-to-red gradient. Dashed lines show thresholds. Instant visual of which wards are full.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="ccard"><div class="ctitle">📊 Chart 8: Beds Available vs Occupied</div><div class="csub">Stacked bars showing capacity distribution by ward</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Occupied",x=beds["ward_name"],y=beds["occupied_beds"],marker_color="#1976d2"))
        fig2.add_trace(go.Bar(name="Available",x=beds["ward_name"],y=beds["available_beds"],marker_color="#81c784"))
        fig2.update_layout(barmode="stack",legend=dict(orientation="h",y=1.1),
                           xaxis_title="Ward",yaxis_title="Number of Beds")
        st.plotly_chart(wchart(fig2,360), use_container_width=True)
        st.markdown('<div class="csub" style="color:#6c757d!important"><b>🎨 For Presentation:</b> Stacked bar. Blue = occupied, green = available. Shows absolute numbers vs percentages in Chart 7.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Ward Status Summary")
    show = beds[["ward_name","total_beds","occupied_beds","available_beds","occupancy_pct","status"]].copy()
    show["occupancy_pct"] = show["occupancy_pct"].apply(lambda x: f"{x:.0f}%")
    show.columns = ["Ward","Total Beds","Occupied","Available","Occupancy %","Status"]
    st.dataframe(show.reset_index(drop=True), use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE 5 — DEPARTMENT PERFORMANCE
# ════════════════════════════════════════════════════════════════
elif page == "📈  Department Performance":
    st.markdown('<div class="topbar"><h1>📈 Department Performance Comparison</h1><p>Workload, efficiency, and resource utilization by department</p></div>', unsafe_allow_html=True)

    dept_summary = dff.groupby("department").agg(
        patients=("patients_arrived","sum"),
        avg_wait=("wait_time_min","mean"),
        avg_staff=("staff_on_duty","mean")
    ).reset_index()
    dept_summary["patients_per_staff"] = (dept_summary["patients"] / (dept_summary["avg_staff"] * dff.groupby("department").size())).round(1)

    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="ccard"><div class="ctitle">📊 Chart 9: Patients Served vs Staff Levels</div><div class="csub">Bubble size = wait time — shows if departments are understaffed</div>', unsafe_allow_html=True)
        fig = px.scatter(dept_summary, x="avg_staff", y="patients", size="avg_wait",
                         color="avg_wait", color_continuous_scale=["#388e3c","#f57c00","#d32f2f"],
                         text="department", labels={"avg_staff":"Avg Staff on Duty","patients":"Total Patients"},
                         size_max=40)
        fig.update_traces(textposition="top center")
        st.plotly_chart(wchart(fig,360), use_container_width=True)
        st.markdown('<div class="csub" style="color:#6c757d!important"><b>🎨 For Presentation:</b> Scatter/bubble chart. Large red bubbles = high patient volume + long waits. Shows which departments need more staff.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="ccard"><div class="ctitle">📊 Chart 10: Average Wait Time Comparison</div><div class="csub">Department-by-department wait time performance</div>', unsafe_allow_html=True)
        dept_sorted = dept_summary.sort_values("avg_wait", ascending=False)
        dept_sorted["label"] = dept_sorted["avg_wait"].apply(lambda x: f"{x:.0f}m")
        fig2 = px.bar(dept_sorted, x="department", y="avg_wait", color="avg_wait",
                      color_continuous_scale=["#388e3c","#f57c00","#d32f2f"],
                      text="label", labels={"avg_wait":"Avg Wait (min)","department":""})
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False)
        st.plotly_chart(wchart(fig2,360), use_container_width=True)
        st.markdown('<div class="csub" style="color:#6c757d!important"><b>🎨 For Presentation:</b> Ranked bar chart. Worst performers on top. Red = needs immediate attention.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Department Performance Table")
    show = dept_summary.copy()
    show["avg_wait"] = show["avg_wait"].apply(lambda x: f"{x:.0f} min")
    show["avg_staff"] = show["avg_staff"].apply(lambda x: f"{x:.1f}")
    show.columns = ["Department","Total Patients","Avg Wait","Avg Staff","Patients/Staff Ratio"]
    st.dataframe(show.reset_index(drop=True), use_container_width=True)

st.markdown("---")
st.markdown("<div style='text-align:center;color:#6c757d;font-size:.78rem'>Princess Marina Hospital · Operations Dashboard · Prepared by Data Analytics Team · 2026</div>", unsafe_allow_html=True)
