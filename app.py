import streamlit as st
import speech_recognition as sr
import tempfile, os
from audio_recorder_streamlit import audio_recorder
from emergency_data import classify_severity

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Golden Hour", layout="centered")

# ---------------- HEADER ----------------
st.title("🚨 Golden Hour")
st.subheader("AI Emergency Decision Assistant")
st.write("Get instant guidance during medical emergencies.")
st.divider()

# ---------------- SESSION STATE ----------------
st.session_state.setdefault("all_options", [
    "Road Accident", "Heavy Bleeding", "Chest Pain",
    "Breathing Problem", "Burn Injury", "Fever",
    "Headache", "Stomach Ache", "Dizziness"
])
st.session_state.setdefault("selected_problems", [])
st.session_state.setdefault("custom_input", "")
st.session_state.setdefault("voice_text", "")

# ---------------- HELPERS ----------------
def normalize_and_split(text):
    for sep in [" and ", ",", "&"]:
        text = text.replace(sep, "|")
    return [i.strip().title() for i in text.split("|") if i.strip()]

def add_problems(text):
    for p in normalize_and_split(text):
        if p not in st.session_state.all_options:
            st.session_state.all_options.append(p)
        if p not in st.session_state.selected_problems:
            st.session_state.selected_problems.append(p)

# ---------------- PROBLEM SELECTION ----------------
st.write("## What is the emergency?")
st.multiselect(
    "Select all that apply",
    st.session_state.all_options,
    key="selected_problems"
)

# ---------------- TEXT INPUT ----------------
col1, col2 = st.columns([3, 1])
with col1:
    user_text = st.text_input("➕ Add your problem", placeholder="fever and headache")
with col2:
    if st.button("Add Text"):
        add_problems(user_text)
        st.rerun()

# ---------------- VOICE INPUT ----------------
st.divider()
st.write("🎙️ Describe the problem using voice")

audio_bytes = audio_recorder("Click to record")

if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        audio_path = f.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        st.session_state.voice_text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        st.error("Could not understand the audio")
    finally:
        os.remove(audio_path)

if st.session_state.voice_text:
    if st.button("➕ Add Voice Input"):
        add_problems(st.session_state.voice_text)
        st.session_state.voice_text = ""
        st.rerun()

# ---------------- VALIDATION ----------------
if not st.session_state.selected_problems:
    st.info("Please report at least one problem.")
    st.stop()

# ---------------- SEVERITY CHECK ----------------
severity = "Urgent"
for p in st.session_state.selected_problems:
    if classify_severity(p) == "Severe":
        severity = "Severe"
        break

def maps_link(level):
    q = "trauma hospital near me" if level == "Severe" else "hospital near me"
    return f"https://www.google.com/maps/search/{q.replace(' ', '+')}"

# ---------------- OUTPUT ----------------
st.divider()

if severity == "Severe":
    st.error("🔴 SEVERE EMERGENCY")
    st.write("📞 Call emergency services immediately")
    st.write("🩸 Provide first aid")
    st.write("🏥 Reach nearest trauma hospital")
    st.markdown(f"[🧭 Find Trauma Hospitals]({maps_link(severity)})")

else:
    st.warning("🟠 URGENT MEDICAL ATTENTION NEEDED")
    st.write("🏥 Visit a nearby clinic")
    st.markdown(f"[🧭 Find Hospitals]({maps_link(severity)})")

st.divider()
st.write("### Reported Problems:")
for p in st.session_state.selected_problems:
    st.write(f"• {p}")
