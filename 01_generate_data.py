"""
PRINCESS MARINA HOSPITAL — DATA GENERATOR
Run this FIRST before anything else.
Generates 6 months of realistic patient flow, inventory, and bed occupancy data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

print("=" * 70)
print("PRINCESS MARINA HOSPITAL — GENERATING OPERATIONAL DATA")
print("=" * 70)

# ── CONFIGURATION ─────────────────────────────────────────────────
START_DATE = datetime(2025, 7, 1)
END_DATE   = datetime(2025, 12, 31)
DAYS       = (END_DATE - START_DATE).days + 1

DEPARTMENTS = ["Emergency", "Outpatient", "Surgery", "Maternity", "Pediatrics", "ICU"]
SHIFTS      = ["Morning (7am-3pm)", "Afternoon (3pm-11pm)", "Night (11pm-7am)"]
DAYS_WEEK   = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

print(f"\n  Generating {DAYS} days of operational data...")

# ═════════════════════════════════════════════════════════════════
# PART 1: PATIENT FLOW DATA (Daily traffic by department)
# ═════════════════════════════════════════════════════════════════
print("\n[1/3] Generating patient flow data...")

patient_flow = []
for day_offset in range(DAYS):
    current_date = START_DATE + timedelta(days=day_offset)
    day_name     = DAYS_WEEK[current_date.weekday()]
    is_weekend   = day_name in ("Saturday", "Sunday")
    
    for dept in DEPARTMENTS:
        for shift in SHIFTS:
            # Base patient volume varies by dept and shift
            base_volume = {
                "Emergency":  {"Morning (7am-3pm)": 45, "Afternoon (3pm-11pm)": 55, "Night (11pm-7am)": 35},
                "Outpatient": {"Morning (7am-3pm)": 80, "Afternoon (3pm-11pm)": 60, "Night (11pm-7am)": 0},
                "Surgery":    {"Morning (7am-3pm)": 8,  "Afternoon (3pm-11pm)": 6,  "Night (11pm-7am)": 2},
                "Maternity":  {"Morning (7am-3pm)": 12, "Afternoon (3pm-11pm)": 15, "Night (11pm-7am)": 10},
                "Pediatrics": {"Morning (7am-3pm)": 30, "Afternoon (3pm-11pm)": 25, "Night (11pm-7am)": 15},
                "ICU":        {"Morning (7am-3pm)": 8,  "Afternoon (3pm-11pm)": 8,  "Night (11pm-7am)": 8},
            }[dept][shift]
            
            # Weekend adjustment (less outpatient, more emergency)
            if is_weekend:
                if dept == "Outpatient": base_volume = int(base_volume * 0.4)
                if dept == "Emergency":  base_volume = int(base_volume * 1.3)
            
            # Random variation
            patients_arrived = max(0, int(base_volume + random.gauss(0, base_volume * 0.15)))
            
            # Staff on duty
            staff_ratio = {"Emergency": 6, "Outpatient": 4, "Surgery": 3, "Maternity": 4, "Pediatrics": 5, "ICU": 2}
            staff_on_duty = max(1, int(patients_arrived / staff_ratio[dept]) + random.randint(-1, 1))
            
            # Wait time (inversely related to staff-to-patient ratio)
            ratio = patients_arrived / staff_on_duty if staff_on_duty > 0 else patients_arrived
            base_wait = max(5, min(120, ratio * 3 + random.gauss(0, 8)))
            wait_time_min = round(base_wait, 1)
            
            patient_flow.append({
                "date":             current_date.strftime("%Y-%m-%d"),
                "day_of_week":      day_name,
                "shift":            shift,
                "department":       dept,
                "patients_arrived": patients_arrived,
                "staff_on_duty":    staff_on_duty,
                "wait_time_min":    wait_time_min,
            })

df_flow = pd.DataFrame(patient_flow)
df_flow.to_csv("patient_flow.csv", index=False)
print(f"  ✅  {len(df_flow):,} patient flow records generated")

# ═════════════════════════════════════════════════════════════════
# PART 2: INVENTORY DATA (Medications and supplies)
# ═════════════════════════════════════════════════════════════════
print("\n[2/3] Generating inventory data...")

MEDICATIONS = [
    ("Paracetamol 500mg", 5000, 90, 2.50),
    ("Ibuprofen 400mg", 3000, 90, 3.80),
    ("Amoxicillin 250mg", 2500, 60, 12.50),
    ("Metformin 500mg", 4000, 180, 8.20),
    ("Amlodipine 5mg", 3500, 180, 6.50),
    ("Omeprazole 20mg", 2000, 90, 15.00),
    ("Ciprofloxacin 500mg", 1500, 60, 22.00),
    ("Azithromycin 500mg", 1200, 60, 28.00),
    ("Insulin (10ml vial)", 400, 30, 85.00),
    ("Salbutamol Inhaler", 600, 90, 45.00),
    ("Hydrocortisone Cream", 800, 90, 18.50),
    ("Diclofenac 50mg", 2000, 90, 7.20),
    ("Furosemide 40mg", 1800, 180, 5.50),
    ("Atenolol 50mg", 2200, 180, 4.80),
    ("IV Fluid (1L)", 3000, 180, 12.00),
    ("Gauze Pads (box)", 5000, 365, 8.00),
    ("Syringes (box of 100)", 4000, 365, 25.00),
    ("Gloves (box of 100)", 8000, 365, 15.00),
]

inventory = []
snapshot_date = END_DATE
for med_name, stock_qty, shelf_life_days, unit_cost in MEDICATIONS:
    # Expiry date
    days_remaining = random.randint(10, shelf_life_days)
    expiry_date = snapshot_date + timedelta(days=days_remaining)
    
    # Usage rate (units per day)
    daily_usage = random.randint(int(stock_qty * 0.005), int(stock_qty * 0.02))
    
    # Days until stockout
    days_until_stockout = int(stock_qty / daily_usage) if daily_usage > 0 else 999
    
    # Flags
    expiring_soon = 1 if days_remaining <= 30 else 0
    low_stock     = 1 if days_until_stockout <= 14 else 0
    
    # Value at risk (if expiring)
    value_at_risk = stock_qty * unit_cost if expiring_soon else 0
    
    inventory.append({
        "item_name":           med_name,
        "stock_quantity":      stock_qty,
        "unit_cost_bwp":       unit_cost,
        "total_value_bwp":     stock_qty * unit_cost,
        "expiry_date":         expiry_date.strftime("%Y-%m-%d"),
        "days_until_expiry":   days_remaining,
        "expiring_soon":       expiring_soon,
        "daily_usage_rate":    daily_usage,
        "days_until_stockout": days_until_stockout,
        "low_stock":           low_stock,
        "value_at_risk_bwp":   value_at_risk,
    })

df_inv = pd.DataFrame(inventory)
df_inv.to_csv("inventory.csv", index=False)
print(f"  ✅  {len(df_inv):,} inventory items tracked")
print(f"  ✅  Items expiring within 30 days: {df_inv['expiring_soon'].sum()}")
print(f"  ✅  Total value at risk: P{df_inv['value_at_risk_bwp'].sum():,.2f}")

# ═════════════════════════════════════════════════════════════════
# PART 3: BED OCCUPANCY DATA (Real-time bed tracking)
# ═════════════════════════════════════════════════════════════════
print("\n[3/3] Generating bed occupancy data...")

WARDS = {
    "General Ward A": 40,
    "General Ward B": 40,
    "Maternity": 25,
    "Pediatrics": 30,
    "ICU": 12,
    "Surgery Recovery": 20,
}

bed_data = []
for ward_name, total_beds in WARDS.items():
    # Base occupancy varies by ward
    base_occ = {"General Ward A": 0.82, "General Ward B": 0.78, "Maternity": 0.85,
                "Pediatrics": 0.70, "ICU": 0.95, "Surgery Recovery": 0.65}[ward_name]
    
    occupied = int(total_beds * base_occ + random.randint(-3, 3))
    occupied = max(0, min(total_beds, occupied))
    available = total_beds - occupied
    occupancy_pct = round(occupied / total_beds * 100, 1)
    
    # Average length of stay (days)
    avg_los = {"General Ward A": 5.2, "General Ward B": 4.8, "Maternity": 2.5,
               "Pediatrics": 3.8, "ICU": 7.5, "Surgery Recovery": 2.2}[ward_name]
    
    # Estimated turnover (beds freed per day)
    turnover = round(occupied / avg_los, 1)
    
    bed_data.append({
        "ward_name":           ward_name,
        "total_beds":          total_beds,
        "occupied_beds":       occupied,
        "available_beds":      available,
        "occupancy_pct":       occupancy_pct,
        "avg_length_of_stay":  avg_los,
        "daily_turnover_rate": turnover,
        "status": "At Capacity" if occupancy_pct > 90 else "High Occupancy" if occupancy_pct > 75 else "Normal",
    })

df_beds = pd.DataFrame(bed_data)
df_beds.to_csv("bed_occupancy.csv", index=False)
print(f"  ✅  {len(df_beds)} wards tracked")
print(f"  ✅  Total beds: {df_beds['total_beds'].sum()}")
print(f"  ✅  Overall occupancy: {df_beds['occupied_beds'].sum() / df_beds['total_beds'].sum() * 100:.1f}%")

# ── SUMMARY ───────────────────────────────────────────────────────
print("\n" + "─"*70)
print("DATA GENERATION COMPLETE")
print("─"*70)
print(f"  📂 patient_flow.csv     : {len(df_flow):,} records")
print(f"  📂 inventory.csv        : {len(df_inv):,} items")
print(f"  📂 bed_occupancy.csv    : {len(df_beds):,} wards")
print(f"\n  Next: python 02_eda_ml.py")
print("=" * 70)
