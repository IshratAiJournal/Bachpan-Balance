
import streamlit as st
import datetime
import os
import pandas as pd

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="Bachpan Balance", layout="centered")
st.title("🌟 Bachpan Balance")
st.subheader("Track your child’s daily routine with love and discipline 💖")

# ---------- DATA SETUP ----------
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "bachpan_log.csv")
os.makedirs(DATA_DIR, exist_ok=True)

# Daily activities we want to track
ACTIVITIES = [
    "Drank 4 glasses of water",
    "Ate 1 apple",
    "Ate 1 egg",
    "Homework completed",
    "Outdoor playtime done",
    "Indoor playtime done",
    "Bedtime story read",
    "Spiritual education given",
    "Sports activity done",
    "Prepared for exams/competitions",
    "Limited screen time maintained",
]

# ---------- INPUTS (TOP BAR) ----------
colA, colB = st.columns([1,1])
with colA:
    child_name = st.text_input("👶 Child Name", value="Imad")
with colB:
    selected_date = st.date_input("📅 Select Date", datetime.date.today())

st.markdown("## ✅ Daily Checklist")

# We’ll store choices and optional notes
choices = {}
notes = {}

completed_count = 0
for activity in ACTIVITIES:
    key_base = f"{child_name}_{selected_date}_{activity}".replace(" ", "_")
    c1, c2 = st.columns([2,2])
    with c1:
        checked = st.checkbox(activity, key=key_base+"_check")
        choices[activity] = checked
        if checked:
            completed_count += 1
    with c2:
        note = st.text_input(f"📝 Notes for {activity}", key=key_base+"_note", placeholder="(optional)")
        notes[activity] = note

# ---------- SUBMIT ----------
if st.button("🎯 Submit"):
    total = len(ACTIVITIES)
    percent = round((completed_count/total)*100)

    # Give feedback
    st.success(f"Great job, {child_name}! {completed_count}/{total} tasks completed on {selected_date}. ({percent}%) 🌈")
    st.progress(completed_count/total)
    if completed_count == total:
        st.balloons()

    # Build one row for CSV (wide format: each activity is a column)
    row = {
        "date": str(selected_date),
        "child": child_name,
        "completed": completed_count,
        "total": total,
        "percent": percent
    }
    # Add activity yes/no and notes
    for activity in ACTIVITIES:
        row[f"{activity}"] = "Yes" if choices[activity] else "No"
        if notes[activity]:
            row[f"{activity} - note"] = notes[activity]

    # Append to CSV (create header if file doesn't exist)
    df = pd.DataFrame([row])
    write_header = not os.path.exists(DATA_FILE)
    df.to_csv(DATA_FILE, mode="a", index=False, header=write_header)

    # Show a mini summary table for today
    st.markdown("### 📋 Saved Summary (Today)")
    st.dataframe(df)

# ---------- TIP ----------
st.caption("Tip: Your data is saved in data/bachpan_log.csv. Keep using the app daily to build healthy habits! ✅")
