# Bachpan_Balance — Streamlit App (v1.1: Gender + Personal Water Intake)
# ------------------------------------------------------------
# How to run locally (after saving this file as app.py):
# 1) pip install streamlit
# 2) streamlit run app.py
# ------------------------------------------------------------

import os
import json
import math
import datetime as dt
from typing import Dict, Any

import streamlit as st

# ---------------------------
# Basic setup
# ---------------------------
st.set_page_config(
    page_title="Bachpan Balance",
    page_icon="🧒",
)

# ---------------------------
# Helpers: storage
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
    "created": None,
    "streak": 0,
    "last_day": None,
    "xp": 0,
    "badges": {},   # e.g. {"hydration": "Silver"}
}

def load_profile(name: str) -> Dict[str, Any]:
    path = _user_file(name)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    data = DEFAULT_PROFILE.copy()
    data["name"] = name
    data["created"] = dt.date.today().isoformat()
    return data

def save_profile(profile: Dict[str, Any]):
    path = _user_file(profile.get("name", "guest"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

# ---------------------------
# Content helpers
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
}

PROTEIN_OPTIONS = [
    "Egg",
    "Paneer",
    "Dal/Lentils",
    "Soya Chunks",
    "Chickpeas",
    "Peanut Butter",
]

OUTDOOR_OPTIONS = ["Football", "Cricket", "Swimming", "Running", "Cycling", "Free Play"]
INDOOR_OPTIONS = ["Free Play", "Drawing", "Painting", "Chess", "Carom", "Craft"]

BADGE_LADDER = ["Bronze", "Silver", "Gold", "Legend"]

THRESHOLDS = {
    "hydration": [0.25, 0.5, 0.8, 1.0],
}

BADGE_TITLES = {
    # Hydration
    "hydration": {
        "Bronze": ("Drop Collector", "Every drop counts!"),
        "Silver": ("Wave Rider", "Stay cool, stay strong!"),
        "Gold": ("Ocean Guardian", "You’re mastering hydration!"),
        "Legend": ("Ice Monarch", "You rule the world of water!"),
    },
    # Fruit
    "fruit": {
        "Bronze": ("Fruit Explorer", "One fruit makes you smarter!"),
        "Silver": ("Fruit Ninja", "Slicing health into your day!"),
        "Gold": ("Vitamin Hero", "Energy booster unlocked!"),
        "Legend": ("Rainbow Eater", "Colors of health unlocked!"),
    },
    # Protein
    "protein": {
        "Bronze": ("Protein Starter", "Strong muscles begin here!"),
        "Silver": ("Power Builder", "Your body is growing stronger!"),
        "Gold": ("Muscle Knight", "Protein power active!"),
        "Legend": ("Strength Superhero", "Unstoppable energy!"),
    },
    # School work
    "school": {
        "Bronze": ("Task Finisher", "Great job completing work!"),
        "Silver": ("Smart Learner", "Knowledge is your superpower!"),
        "Gold": ("Brain Master", "Your focus shines!"),
        "Legend": ("Wisdom Wizard", "Legend of learning!"),
    },
    # Outdoor
    "outdoor": {
        "Bronze": ("Playtime Champ", "Fun makes you strong!"),
        "Silver": ("Energy Explorer", "Faster and fitter!"),
        "Gold": ("Fitness Hero", "Your energy inspires!"),
        "Legend": ("Sunshine Legend", "Nature salutes you!"),
    },
    # Indoor
    "indoor": {
        "Bronze": ("Art Friend", "Creativity unlocked!"),
        "Silver": ("Imagination Champ", "Ideas sparkle!"),
        "Gold": ("Mind Game Hero", "Sharp and playful!"),
        "Legend": ("Creative Legend", "Worlds of wonder!"),
    },
    # Exam prep
    "exam": {
        "Bronze": ("Smart Stepper", "Small steps → big difference!"),
        "Silver": ("Brain Booster", "Your brain grows daily!"),
        "Gold": ("Knowledge Hero", "Preparation = confidence!"),
        "Legend": ("Exam Conqueror", "Ready for success!"),
    },
    # Screen
    "screen": {
        "Bronze": ("Screen Smart Kid", "You use tech wisely!"),
        "Silver": ("Idea Maker", "Screens create ideas!"),
        "Gold": ("Digital Hero", "You build, not just watch!"),
        "Legend": ("Tech Mastermind", "You invent the future!"),
    },
}

# ---------------------------
# Utility logic
# ---------------------------
def calculate_water_intake(age: int, gender: str, weight: float, height: float) -> Dict[str, Any]:
    """
    Return recommended daily water intake in ml, liters, and glasses.
    Approach:
    - Use weight-based estimate (ml_per_kg), then ensure minimums by age/gender.
    - This is a general guideline — adapt if you have medical advice.
    """
    try:
        weight = float(weight) if weight else 0.0
    except Exception:
        weight = 0.0

    # base by weight (ml per kg)
    # Using 35 ml/kg as a reasonable middle-ground for children
    if weight > 0:
        base_ml = weight * 35
    else:
        base_ml = 1200  # fallback

    # Minimum recommendations (approximate)
    if age <= 3:
        min_ml = 1000  # 1.0 L
    elif 4 <= age <= 8:
        min_ml = 1200  # 1.2 L
    elif 9 <= age <= 13:
        # small difference by gender
        min_ml = 1400 if gender.lower() == "girl" else 1600
    elif 14 <= age <= 18:
        min_ml = 1800 if gender.lower() == "girl" else 2400
    else:
        min_ml = 2000

    water_ml = max(base_ml, min_ml)

    glass_ml = 250  # definition for glasses
    glasses = math.ceil(water_ml / glass_ml)

    return {
        "ml": int(round(water_ml)),
        "liters": round(water_ml / 1000, 2),
        "glasses": int(glasses),
        "glass_ml": int(glass_ml),
    }

def award_level(progress_ratio: float) -> str:
    levels = BADGE_LADDER
    th = THRESHOLDS["hydration"]
    if progress_ratio >= th[3]:
        return levels[3]
    elif progress_ratio >= th[2]:
        return levels[2]
    elif progress_ratio >= th[1]:
        return levels[1]
    elif progress_ratio >= th[0]:
        return levels[0]
    return ""

def xp_for(action: str) -> int:
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
    return table.get(action, 1)

# ---------------------------
# UI components
# ---------------------------
st.title("🧒 Bachpan Balance")
st.caption("Playful daily habits for strong bodies and bright minds ✨")

with st.sidebar:
    st.header("Parent Mode")
    parent_limit = st.number_input("Daily screen limit (minutes)", min_value=0, max_value=300, value=60, step=5)
    st.info("Tip: Aim for balanced usage — create first, then enjoy fun time.")

name = st.text_input("Child's Name", placeholder="Type your name here…")

if not name.strip():
    st.warning("Please type your name to start.")
    st.stop()

profile = load_profile(name)

# Input row: Gender, Age
col1, col2 = st.columns([1,1])
with col1:
    # pre-select gender if exists
    default_gender = profile.get("gender") or "Boy"
    gender = st.radio("Gender", ["Boy", "Girl", "Other"], index=["Boy","Girl","Other"].index(default_gender) if default_gender in ["Boy","Girl","Other"] else 0)
with col2:
    age = st.number_input("Age (years)", min_value=1, max_value=17, value=int(profile.get("age") or 8))

# Next row: weight, height
col3, col4 = st.columns([1,1])
with col3:
    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=120.0, value=float(profile.get("weight") or 25.0), step=0.5)
with col4:
    height = st.number_input("Height (cm)", min_value=70.0, max_value=200.0, value=float(profile.get("height") or 120.0), step=0.5)

# save basics into profile
profile.update({
    "gender": gender,
    "age": int(age),
    "weight": float(weight),
    "height": float(height),
})

# Water recommendation using new function
water_rec = calculate_water_intake(int(age), gender, float(weight), float(height))

# Prepare today's record (keep any existing data)
TODAY = dt.date.today().isoformat()
existing_day = profile.get(TODAY)
day = existing_day or {
    "water": {"glasses": 0, "target_glasses": water_rec["glasses"], "target_ml": water_rec["ml"]},
    "fruit": {"items": []},
    "protein": {"items": []},
    "school_work": False,
    "outdoor": [],
    "indoor": [],
    "exam_prep_min": 0,
    "screen": {"create": 0, "fun": 0, "limit": parent_limit},
    "completed": False,
}
# If existing_day exists but lacks the new fields, ensure they exist
if "water" not in day:
    day["water"] = {"glasses": 0, "target_glasses": water_rec["glasses"], "target_ml": water_rec["ml"]}
else:
    # update today's targets to current calculation (so they reflect new inputs)
    day["water"].setdefault("glasses", 0)
    day["water"]["target_glasses"] = water_rec["glasses"]
    day["water"]["target_ml"] = water_rec["ml"]

profile[TODAY] = day

st.divider()

# ---------------------------
# Hydration section
# ---------------------------
st.subheader("💧 Water Intake")

colA, colB, colC = st.columns(3)
with colA:
    st.metric("Target (ml)", day["water"].get("target_ml", water_rec["ml"]))
with colB:
    st.metric("Target (liters)", water_rec["liters"])
with colC:
    st.metric("Target (glasses)", day["water"].get("target_glasses", water_rec["glasses"]))

st.metric("Glasses Drank", day["water"].get("glasses", 0))

# compute left
glass_size = water_rec.get("glass_ml", 250)
drank_ml = day["water"].get("glasses", 0) * glass_size
left_ml = max(0, day["water"].get("target_ml", water_rec["ml"]) - drank_ml)
left_glasses = math.ceil(left_ml / glass_size) if left_ml > 0 else 0

colL, colR = st.columns(2)
with colL:
    st.metric("Left (ml)", left_ml)
with colR:
    st.metric("Left (glasses)", left_glasses)

if st.button("I drank 1 glass"):
    day["water"]["glasses"] = day["water"].get("glasses", 0) + 1
    profile["xp"] += xp_for("water_glass")

progress = min(1.0, day["water"].get("glasses", 0) / max(1, day["water"].get("target_glasses", water_rec["glasses"])))
st.progress(progress, text=f"Hydration progress: {int(progress*100)}%")

level = award_level(progress)
if level:
    title, line = BADGE_TITLES["hydration"][level]
    st.success(f"🏅 {title} — {line}")
    profile.setdefault("badges", {})["hydration"] = level

st.caption("Tip: Drink water regularly. We show ml + liters + glasses (1 glass = 250 ml).")

st.divider()

# ---------------------------
# Fruit section
# ---------------------------
st.subheader("🍎 I ate fruit")
fruit_choice = st.selectbox("Pick a fruit you ate", options=list(FRUIT_BENEFITS.keys()) + ["Other"])
other_fruit = ""
if fruit_choice == "Other":
    other_fruit = st.text_input("Type fruit name")

if st.button("Add fruit"):
    item = other_fruit.strip() if fruit_choice == "Other" else fruit_choice
    if item:
        day["fruit"]["items"].append(item)
        profile["xp"] += xp_for("fruit")

if day["fruit"]["items"]:
    st.write("**Today's fruits:** ", ", ".join(day["fruit"]["items"]))
    f = day["fruit"]["items"][-1]
    benefit = FRUIT_BENEFITS.get(f, "Great choice! Fruits give you power.")
    st.info(f"🎉 Awesome! {f} — {benefit}")

fruit_count = len(day["fruit"]["items"])  # simple: 1=Bronze, 2=Silver, 3=Gold, 4+=Legend
if fruit_count >= 1:
    lvl = BADGE_LADDER[min(3, fruit_count-1)]
    title, line = BADGE_TITLES["fruit"][lvl]
    st.success(f"🏅 {title} — {line}")
    profile["badges"]["fruit"] = lvl

st.divider()

# ---------------------------
# Protein section
# ---------------------------
st.subheader("💪 Protein Power")
protein_sel = st.multiselect("Choose what you ate", options=PROTEIN_OPTIONS)
if st.button("Save protein"):
    day["protein"]["items"] = list(set(day["protein"]["items"] + protein_sel))
    if protein_sel:
        profile["xp"] += xp_for("protein")

if day["protein"]["items"]:
    st.write("**Today's protein foods:** ", ", ".join(day["protein"]["items"]))
    count = len(day["protein"]["items"])  # 1=Bronze ... 4+=Legend
    lvl = BADGE_LADDER[min(3, count-1)]
    title, line = BADGE_TITLES["protein"][lvl]
    st.success(f"🏅 {title} — {line}")
    profile["badges"]["protein"] = lvl

st.divider()

# ---------------------------
# School work
# ---------------------------
st.subheader("📘 School Work")
school_done = st.checkbox("I finished today's school work", value=bool(day["school_work"]))
if school_done and not day["school_work"]:
    profile["xp"] += xp_for("school")

day["school_work"] = school_done
if school_done:
    title, line = BADGE_TITLES["school"]["Bronze"]
    st.success(f"🏅 {title} — {line}")

st.divider()

# ---------------------------
# Outdoor play
# ---------------------------
st.subheader("🌞 Outdoor Play")
outdoor_sel = st.multiselect("What did you play today?", options=OUTDOOR_OPTIONS, default=day["outdoor"])
if st.button("Save outdoor play"):
    day["outdoor"] = outdoor_sel
    if outdoor_sel:
        profile["xp"] += xp_for("outdoor")

if day["outdoor"]:
    st.write("**Outdoor:** ", ", ".join(day["outdoor"]))
    lvl = BADGE_LADDER[min(3, len(day["outdoor"]) - 1)]
    title, line = BADGE_TITLES["outdoor"][lvl]
    st.success(f"🏅 {title} — {line}")

st.divider()

# ---------------------------
# Indoor play
# ---------------------------
st.subheader("🏠 Indoor Play")
indoor_sel = st.multiselect("What did you play/create today?", options=INDOOR_OPTIONS, default=day["indoor"])
if st.button("Save indoor play"):
    day["indoor"] = indoor_sel
    if indoor_sel:
        profile["xp"] += xp_for("indoor")

if day["indoor"]:
    st.write("**Indoor:** ", ", ".join(day["indoor"]))
    lvl = BADGE_LADDER[min(3, len(day["indoor"]) - 1)]
    title, line = BADGE_TITLES["indoor"][lvl]
    st.success(f"🏅 {title} — {line}")

st.divider()

# ---------------------------
# Exam prep
# ---------------------------
st.subheader("📚 Exam Prep")
exam_min = st.number_input("Study minutes today", min_value=0, max_value=600, value=int(day["exam_prep_min"]))
if st.button("Save study time"):
    day["exam_prep_min"] = int(exam_min)
    profile["xp"] += xp_for("exam_5min") * (day["exam_prep_min"] // 5)

if day["exam_prep_min"] > 0:
    lvl = BADGE_LADDER[min(3, day["exam_prep_min"] // 20)]  # 0-19: Bronze, 20-39: Silver, 40-59: Gold, 60+: Legend
    title, line = BADGE_TITLES["exam"][lvl]
    st.success(f"🏅 {title} — {line}")
    st.info("Brain Booster Mode ON! Smart steps → Big success ✨")

st.divider()

# ---------------------------
# Screen time (healthy limit)
# ---------------------------
st.subheader("💻 Screen Time (Balanced)")
create_min = st.number_input("Minutes creating/learning (drawing app, coding, music)", min_value=0, max_value=600, value=int(day["screen"]["create"]))
fun_min = st.number_input("Minutes for fun (shows, games)", min_value=0, max_value=600, value=int(day["screen"]["fun"]))

if st.button("Save screen time"):
    day["screen"]["create"] = int(create_min)
    day["screen"]["fun"] = int(fun_min)
    day["screen"]["limit"] = int(parent_limit)
    profile["xp"] += xp_for("screen_create_10min") * (day["screen"]["create"] // 10)

used = day["screen"]["create"] + day["screen"]["fun"]
limit = day["screen"]["limit"]
remain = max(0, limit - used)

st.metric("Used today (min)", used)
st.metric("Limit (min)", limit)
st.metric("Left (min)", remain)

if used > limit:
    st.error("Time's up! Your eyes need a rest to stay sharp. Try some outdoor or art time now ✨")
else:
    if day["screen"]["create"] >= day["screen"]["fun"]:
        st.success("Screen Smart Creator — You built something before fun. Proud of you!")
    else:
        st.warning("Balance tip: Create first, then enjoy fun time. You can do it!")

st.divider()

# ---------------------------
# XP, Streak & Day completion
# ---------------------------
st.subheader("🌟 Progress & Rewards")

# Simple "day complete" condition: hit water target AND did any two other items
other_hits = 0
other_hits += 1 if day["fruit"]["items"] else 0
other_hits += 1 if day["protein"]["items"] else 0
other_hits += 1 if day["school_work"] else 0
other_hits += 1 if day["outdoor"] else 0
other_hits += 1 if day["indoor"] else 0
other_hits += 1 if day["exam_prep_min"] >= 10 else 0

hydration_met = day["water"].get("glasses", 0) >= day["water"].get("target_glasses", water_rec["glasses"])
allow_complete = hydration_met and other_hits >= 2

colp, colq = st.columns([1,1])
with colp:
    st.metric("XP", profile.get("xp", 0))
with colq:
    st.metric("Streak (days)", profile.get("streak", 0))

if st.button("✅ Mark day complete", disabled=day["completed"] or not allow_complete):
    day["completed"] = True
    today = dt.date.today()
    last = profile.get("last_day")
    if last:
        try:
            last_d = dt.date.fromisoformat(last)
            if (today - last_d).days == 1:
                profile["streak"] = profile.get("streak", 0) + 1
            else:
                profile["streak"] = 1
        except Exception:
            profile["streak"] = 1
    else:
        profile["streak"] = 1
    profile["last_day"] = today.isoformat()
    profile["xp"] += xp_for("day_complete")

if allow_complete and not day["completed"]:
    st.info("Almost there! Hit the button to complete your day and grow your streak 🔥")
elif day["completed"]:
    st.success("Great job! Day completed. See you tomorrow ✨")
else:
    st.warning("Complete your water goal and any two more activities to finish the day.")

st.divider()

# ---------------------------
# Trophy room
# ---------------------------
st.subheader("🏆 Trophy Room")
if profile.get("badges"):
    for section, lvl in profile["badges"].items():
        title, line = BADGE_TITLES.get(section, {}).get(lvl, (section.title(), ""))
        st.write(f"**{section.title()}** — {lvl}: {title} · {line}")
else:
    st.caption("Earn badges by completing activities. Your trophies will appear here!")

# Final save
save_profile(profile)
