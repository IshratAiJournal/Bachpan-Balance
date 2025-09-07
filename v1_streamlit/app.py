import os
import json
import math
import datetime as dt
import streamlit as st

# ---------------------------
# Data Storage Helpers
# ---------------------------
DATA_DIR = "bb_data"
os.makedirs(DATA_DIR, exist_ok=True)

def _user_file(name: str) -> str:
    safe = "".join([c for c in name.strip() if c.isalnum() or c in ("_","-")]) or "guest"
    return os.path.join(DATA_DIR, f"{safe.lower()}.json")

DEFAULT_PROFILE = {
    "name": "",
    "gender": "",
    "age": None,
    "weight": None,
    "height": None,
    "xp": 0,
    "badges": {},
}

def load_profile(name: str):
    path = _user_file(name)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    data = DEFAULT_PROFILE.copy()
    data["name"] = name
    return data

def save_profile(profile):
    path = _user_file(profile.get("name","guest"))
    with open(path,"w",encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

# ---------------------------
# Constants & Options
# ---------------------------
FRUIT_BENEFITS = {
    "Apple": "Good for heart, fiber for digestion.",
    "Banana": "Boosts energy and helps digestion.",
    "Orange": "Vitamin C for immunity.",
    "Mango": "Vitamin A for eyes.",
    "Grapes": "Antioxidants for cells.",
    "Pomegranate": "Iron and antioxidants.",
    "Papaya": "Great for tummy health.",
    "Guava": "High in Vitamin C.",
    "Strawberry": "Good for skin and heart.",
    "Kiwi": "Boosts immunity.",
    "Litchi": "Vitamin C & energy.",
    "Pineapple": "Digestive enzymes inside.",
    "Watermelon": "Hydrating and refreshing.",
    "Custard Apple": "Energy booster.",
    "Plums": "Rich in antioxidants.",
    "Maskmelon": "Vitamin A & hydration.",
    "Pear": "Fiber-rich.",
    "Jamun": "Good for blood sugar.",
    "Apricot": "Vitamin A for eyes."
}

PROTEIN_OPTIONS = ["Egg","Paneer","Dal/Lentils","Soya Chunks","Chickpeas","Peanut Butter"]
OUTDOOR_OPTIONS = ["Football","Cricket","Swimming","Running","Cycling","Free Play"]
INDOOR_OPTIONS = ["Free Play","Drawing","Painting","Chess","Carom","Craft"]
BADGE_LADDER = ["Bronze","Silver","Gold","Legend"]

# ---------------------------
# XP Helper
# ---------------------------
def xp_for(action):
    table = {
        "water_glass": 5,
        "fruit": 8,
        "protein": 8,
        "school": 10,
        "outdoor": 10,
        "indoor": 8,
        "exam_5min": 2,
        "screen_create_10min": 4,
        "day_complete": 30,
    }
    return table.get(action,1)

# ---------------------------
# Water Recommendation
# ---------------------------
def calculate_water_intake(age:int, gender:str, weight:float):
    try:
        age = int(age)
        weight = float(weight)
        gender = gender.lower()
    except:
        age = 8
        weight = 25
        gender = "boy"

    base_ml = weight * 35  

    if age <= 3:
        min_ml = 1000
    elif age <= 8:
        min_ml = 1200
    elif age <= 13:
        min_ml = 1400 if gender=="girl" else 1600
    elif age <= 18:
        min_ml = 1800 if gender=="girl" else 2400
    else:
        min_ml = 2000

    water_ml = max(base_ml, min_ml)
    glass_ml = 250
    glasses = math.ceil(water_ml / glass_ml)

    return {
        "ml": int(round(water_ml)),
        "liters": round(water_ml / 1000, 2),
        "glasses": glasses,
        "glass_ml": glass_ml
    }

# ---------------------------
# Streamlit App UI
# ---------------------------
st.set_page_config(page_title="Bachpan Balance", page_icon="🧒")
st.title("🧒 Bachpan Balance")
st.caption("Playful daily habits for strong bodies and bright minds ✨")

name = st.text_input("Child's Name")
if not name.strip():
    st.warning("Please type your name to start.")
    st.stop()

profile = load_profile(name)

col1, col2 = st.columns(2)
with col1:
    gender_options = ["Boy","Girl","Other"]
    default_gender = profile.get("gender") if profile.get("gender") in gender_options else "Boy"
    gender = st.radio("Gender", gender_options, index=gender_options.index(default_gender))
with col2:
    age = st.number_input("Age (years)", 1, 17, value=int(profile.get("age") or 8))

col3, col4 = st.columns(2)
with col3:
    weight = st.number_input("Weight (kg)", 10.0, 120.0, value=float(profile.get("weight") or 25.0), step=0.5)
with col4:
    height = st.number_input("Height (cm)", 70.0, 200.0, value=float(profile.get("height") or 120.0), step=0.5)

profile.update({"gender": gender, "age": int(age), "weight": float(weight), "height": float(height)})

water_rec = calculate_water_intake(int(age), gender, float(weight))
TODAY = dt.date.today().isoformat()

day = profile.get(TODAY, {
    "water": {"glasses":0, "target_glasses": water_rec["glasses"], "target_ml": water_rec["ml"]},
    "fruit": {"items":[]},
    "protein": {"items":[]},
    "school_work": False,
    "outdoor": [],
    "indoor": [],
    "exam_prep_min": 0,
    "screen": {"create":0, "fun":0},
    "completed": False
})

day["water"]["target_glasses"] = water_rec["glasses"]
day["water"]["target_ml"] = water_rec["ml"]

st.divider()

# 💧 Water Intake
st.subheader("💧 Water Intake")
colA, colB, colC = st.columns(3)
with colA: st.metric("Target (ml)", day["water"]["target_ml"])
with colB: st.metric("Target (liters)", water_rec["liters"])
with colC: st.metric("Target (glasses)", day["water"]["target_glasses"])
st.metric("Glasses Drank", day["water"]["glasses"])

if st.button("I drank 1 glass"):
    day["water"]["glasses"] += 1
    profile["xp"] += xp_for("water_glass")
    st.success("💧 Fantastic! You’re staying hydrated and strong!")

progress = min(1.0, day["water"]["glasses"] / max(1, day["water"]["target_glasses"]))
st.progress(progress, text=f"Hydration progress: {int(progress*100)}%")

st.divider()

# 🍎 Fruits
st.subheader("🍎 Fruits")
fruit_choice = st.selectbox("Pick a fruit you ate", options=list(FRUIT_BENEFITS.keys()) + ["Other"])
other_fruit = ""
if fruit_choice == "Other":
    other_fruit = st.text_input("Type any other fruit")

if st.button("Add fruit"):
    item = other_fruit.strip() if fruit_choice == "Other" else fruit_choice
    if item:
        day["fruit"]["items"].append(item)
        profile["xp"] += xp_for("fruit")
        st.success(f"🍎 Great job! {item} is super healthy!")

if day["fruit"]["items"]:
    st.write("**Today's fruits:** ", ", ".join(day["fruit"]["items"]))
    last_f = day["fruit"]["items"][-1]
    st.info(f"🎉 {last_f} — {FRUIT_BENEFITS.get(last_f, 'Yummy and healthy!')}")

st.divider()

# 💪 Protein
st.subheader("💪 Protein")
protein_sel = st.multiselect("Choose protein you ate", options=PROTEIN_OPTIONS, default=day["protein"]["items"])
if st.button("Save protein"):
    day["protein"]["items"] = list(set(day["protein"]["items"] + protein_sel))
    if protein_sel:
        profile["xp"] += xp_for("protein")
        st.success("💪 Awesome! Protein helps you grow strong!")

if day["protein"]["items"]:
    st.write("**Today's protein foods:** ", ", ".join(day["protein"]["items"]))

st.divider()

# 📘 School Work
st.subheader("📘 School Work")
school_done = st.checkbox("I finished today's school work", value=day["school_work"])
if school_done and not day["school_work"]:
    profile["xp"] += xp_for("school")
    st.success("📚 Well done! Learning builds your bright future!")
day["school_work"] = school_done

st.divider()

# 🌞 Outdoor Play
st.subheader("🌞 Outdoor Play")
outdoor_options_with_other = OUTDOOR_OPTIONS + ["Other"]
outdoor_sel = st.multiselect(
    "Select outdoor activities today",
    options=outdoor_options_with_other,
    default=[act for act in day["outdoor"] if act in OUTDOOR_OPTIONS]
)

other_outdoor = ""
if "Other" in outdoor_sel:
    other_outdoor = st.text_input("Type any other outdoor game/play")

if st.button("Save outdoor play"):
    activities = [act for act in outdoor_sel if act != "Other"]
    if other_outdoor.strip():
        activities.append(other_outdoor.strip())

    day["outdoor"] = activities
    if activities:
        profile["xp"] += xp_for("outdoor")
        st.success("🌞 Amazing! Playing outside keeps you healthy and happy!")

if day["outdoor"]:
    st.info(f"🏞️ Outdoor activities today: {', '.join(day['outdoor'])}")

st.divider()

# 🏠 Indoor Play
st.subheader("🏠 Indoor Play")
indoor_options_with_other = INDOOR_OPTIONS + ["Other"]
indoor_sel = st.multiselect(
    "Select indoor activities today",
    options=indoor_options_with_other,
    default=[act for act in day["indoor"] if act in INDOOR_OPTIONS]
)

other_indoor = ""
if "Other" in indoor_sel:
    other_indoor = st.text_input("Type any other indoor game/play")

if st.button("Save indoor play"):
    activities = [act for act in indoor_sel if act != "Other"]
    if other_indoor.strip():
        activities.append(other_indoor.strip())

    day["indoor"] = activities
    if activities:
        profile["xp"] += xp_for("indoor")
        st.success("🎨 Excellent! Indoor play sparks creativity!")

if day["indoor"]:
    st.info(f"🏡 Indoor activities today: {', '.join(day['indoor'])}")

st.divider()

# 📖 Exam Preparation
st.subheader("📖 Exam Preparation")
exam_min = st.number_input("Minutes studied for exam today", 0, 180, value=day["exam_prep_min"])
if exam_min > day["exam_prep_min"]:
    profile["xp"] += xp_for("exam_5min") * (exam_min - day["exam_prep_min"]) // 5
    if exam_min > 0:
        st.success("🏆 Excellent! Every minute of study makes you smarter!")
day["exam_prep_min"] = exam_min

st.divider()

# ✅ Day Completion & Badges
st.subheader("🏅 Summary & Badges")
day_complete = st.button("Finish Day")
if day_complete and not day["completed"]:
    profile["xp"] += xp_for("day_complete")
    day["completed"] = True
    st.balloons()
    st.success(f"🎉 {name}, you completed your day! Total XP: {profile['xp']}")

xp = profile["xp"]
for badge in BADGE_LADDER:
    if xp >= 100 and badge not in profile["badges"]:
        profile["badges"][badge] = TODAY
        st.success(f"🏅 Congratulations! You earned a {badge} badge!")

profile[TODAY] = day
save_profile(profile)
