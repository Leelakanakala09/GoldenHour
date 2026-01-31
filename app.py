import streamlit as st
from emergency_data import classify_severity
import speech_recognition as sr
import tempfile
import os

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
        "Burn Injury"
    ]

if "selected_problems" not in st.session_state:
    st.session_state.selected_problems = []

if "custom_input" not in st.session_state:
    st.session_state.custom_input = ""

# ---------------- CALLBACK FOR TEXT INPUT ----------------
def add_problem_on_enter():
    value = st.session_state.custom_input.strip()
    if value != "":
        if value not in st.session_state.all_options:
            st.session_state.all_options.append(value)
        if value not in st.session_state.selected_problems:
            st.session_state.selected_problems.append(value)
        st.session_state.custom_input = ""

# ---------------- MULTISELECT (CHIPS) ----------------
st.write("## What is the emergency? (Select all that apply)")

st.session_state.selected_problems = st.multiselect(
    "",
    options=st.session_state.all_options,
    default=st.session_state.selected_problems
)

# ---------------- TEXT INPUT ----------------
st.text_input(
    "➕ Add your problem (type & press Enter)",
    key="custom_input",
    on_change=add_problem_on_enter
)

# ---------------- VOICE INPUT ----------------
st.divider()
st.write("🎙️ Or describe the problem using voice")

audio_file = st.file_uploader("Upload voice recording (WAV)", type=["wav"])

def speech_to_text(audio_path):
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio)
    except:
        return None

if audio_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_file.read())
        temp_path = temp_audio.name

    spoken_text = speech_to_text(temp_path)
    os.remove(temp_path)

    if spoken_text:
        st.success(f"Recognized: {spoken_text}")
        if spoken_text not in st.session_state.all_options:
            st.session_state.all_options.append(spoken_text)
        if spoken_text not in st.session_state.selected_problems:
            st.session_state.selected_problems.append(spoken_text)
    else:
        st.error("Could not recognize speech")

# ---------------- STOP IF NO INPUT ----------------
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
def get_maps_link(severity):
    if severity == "Severe":
        query = "trauma hospital near me"
    else:
        query = "hospital or clinic near me"
    return f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

maps_link = get_maps_link(severity)

# ---------------- SEVERE ----------------
if severity == "Severe":
    st.error("🔴 SEVERE EMERGENCY")

    st.write("### Immediate Actions:")
    st.write("📞 Call emergency services immediately")
    st.write("🩸 Provide basic first aid if possible")
    st.write("🏥 Go to the nearest trauma hospital")

    st.divider()
    st.markdown(f"[🧭 View Nearby Trauma Hospitals]({maps_link})")

    st.divider()
    if st.button("🚨 PANIC MODE"):
        st.error("EMERGENCY MODE ACTIVATED")
        st.write("📢 CALL AMBULANCE NOW")
        st.write("🩸 APPLY PRESSURE / BASIC FIRST AID")
        st.write("🚑 DO NOT DELAY HOSPITAL VISIT")

# ---------------- URGENT ----------------
else:
    st.warning("🟠 URGENT — MEDICAL ATTENTION NEEDED")

    st.write("### Recommended Actions:")
    st.write("🏥 Contact a nearby hospital or clinic")
    st.write("👩‍⚕️ Consult a medical professional")
    st.write("📅 Monitor symptoms and do not ignore them")

    st.divider()
    st.markdown(f"[🧭 View Nearby Hospitals / Clinics]({maps_link})")
