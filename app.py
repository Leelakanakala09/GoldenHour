import streamlit as st
from emergency_data import classify_severity
import speech_recognition as sr
import tempfile
import os
from audio_recorder_streamlit import audio_recorder

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Golden Hour", layout="centered")

# ---------------- HEADER ----------------
st.title("🚨 Golden Hour")
st.subheader("AI Emergency Decision Assistant")
st.write("Get instant guidance during medical emergencies.")

st.divider()

# ---------------- SESSION STATE ----------------
if "all_options" not in st.session_state:
    st.session_state.all_options = [
        "Road Accident",
        "Heavy Bleeding",
        "Chest Pain",
        "Breathing Problem",
        "Burn Injury",
        "Fever",
        "Headache",
        "Stomach Ache",
        "Dizziness"
    ]

if "selected_problems" not in st.session_state:
    st.session_state.selected_problems = []

if "custom_input" not in st.session_state:
    st.session_state.custom_input = ""

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

# ---------------- HELPERS ----------------
def normalize_and_split(text):
    separators = [" and ", ",", "&"]
    items = [text.lower()]
    for sep in separators:
        items = sum([i.split(sep) for i in items], [])
    return [i.strip().title() for i in items if i.strip()]

# ---------------- ADD FUNCTIONS ----------------
def add_problems_from_text(text):
    problems = normalize_and_split(text)
    for p in problems:
        if p not in st.session_state.all_options:
            st.session_state.all_options.append(p)
        if p not in st.session_state.selected_problems:
            st.session_state.selected_problems.append(p)

# ---------------- PROBLEM SELECTION ----------------
st.write("## What is the emergency? (Select all that apply)")

st.multiselect(
    "",
    options=st.session_state.all_options,
    key="selected_problems",
)

# ---------------- TEXT INPUT ----------------
if st.text_input(
    "➕ Add your problem (type & press Enter)",
    key="custom_input",
    placeholder="Example: fever and headache",
):
    add_problems_from_text(st.session_state.custom_input)
    st.session_state.custom_input = ""
    st.rerun()

# ---------------- VOICE INPUT ----------------
st.divider()
st.write("🎙️ Or describe the problem using voice")

audio_bytes = audio_recorder(
    text="Click to record",
    recording_color="#e74c3c",
    neutral_color="#2c3e50",
    icon_name="microphone",
    icon_size="2x",
)

if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        audio_path = f.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        st.session_state.voice_text = recognizer.recognize_google(audio)
    except:
        st.error("Could not recognize speech")

    os.remove(audio_path)

# ---------------- VOICE CONFIRM ----------------
col1, col2 = st.columns([3, 1])

with col1:
    st.text_input(
        "📝 Recognized problem (edit if needed)",
        key="voice_text",
        placeholder="e.g. fever and headache",
    )

with col2:
    if st.button("➕ Add"):
        add_problems_from_text(st.session_state.voice_text)
        st.session_state.pop("voice_text", None)
        st.rerun()

# ---------------- STOP IF EMPTY ----------------
if len(st.session_state.selected_problems) == 0:
    st.info("Please select, type, or speak at least one problem.")
    st.stop()

st.divider()

# ---------------- SEVERITY DECISION ----------------
severity = "Urgent"
for problem in st.session_state.selected_problems:
    if classify_severity(problem) == "Severe":
        severity = "Severe"
        break

# ---------------- MAPS LINK ----------------
def get_maps_link(level):
    query = "trauma hospital near me" if level == "Severe" else "hospital near me"
    return f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

maps_link = get_maps_link(severity)

# ---------------- SEVERE FLOW ----------------
if severity == "Severe":
    st.error("🔴 SEVERE EMERGENCY")

    st.write("### Immediate Actions:")
    st.write("📞 Call emergency services immediately")
    st.write("🩸 Provide basic first aid if possible")
    st.write("🏥 Go to the nearest trauma hospital")

    st.markdown(f"[🧭 View Nearby Trauma Hospitals]({maps_link})")

    if st.button("🚨 PANIC MODE"):
        st.error("EMERGENCY MODE ACTIVATED")
        st.write("📢 CALL AMBULANCE NOW")
        st.write("🩸 APPLY PRESSURE / BASIC FIRST AID")
        st.write("🚑 DO NOT DELAY HOSPITAL VISIT")

# ---------------- URGENT FLOW ----------------
else:
    st.warning("🟠 URGENT — MEDICAL ATTENTION NEEDED")

    st.write("### Recommended Actions:")
    st.write("🏥 Contact a nearby hospital or clinic")
    st.write("👩‍⚕️ Consult a medical professional")

    st.markdown(f"[🧭 View Nearby Hospitals]({maps_link})")

# ---------------- DISPLAY ----------------
st.divider()
st.write("### Reported Problems:")
for p in st.session_state.selected_problems:
    st.write(f"• {p}")
