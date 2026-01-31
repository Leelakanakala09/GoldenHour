import streamlit as st
import speech_recognition as sr
import tempfile, os
from audio_recorder_streamlit import audio_recorder
from emergency_data import classify_severity

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Golden Hour", layout="wide")

# ---------------- INIT STATE ----------------
def init():
    defaults = {
        "options": [
            "Road Accident", "Heavy Bleeding", "Chest Pain",
            "Breathing Problem", "Burn Injury", "Fever",
            "Headache", "Stomach Ache", "Dizziness"
        ],
        "ui_selected": [],
        "all_symptoms": [],
        "typed_text": "",
        "voice_text": ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

# ---------------- HELPERS ----------------
def split_text(text):
    for sep in [",", "&", " and "]:
        text = text.replace(sep, "|")
    return [t.strip().title() for t in text.split("|") if t.strip()]

def add_symptoms(items):
    for s in items:
        if s not in st.session_state.options:
            st.session_state.options.append(s)
        if s not in st.session_state.all_symptoms:
            st.session_state.all_symptoms.append(s)

# ---------------- HEADER ----------------
st.title("🚨 Golden Hour")
st.subheader("AI Emergency Decision Assistant")
st.divider()

main, side = st.columns([3, 1])

# ================= MAIN =================
with main:

    # -------- MULTISELECT --------
    st.write("### Select symptoms")
    st.multiselect(
        "",
        st.session_state.options,
        key="ui_selected"
    )

    if st.session_state.ui_selected:
        add_symptoms(st.session_state.ui_selected)

    # -------- TEXT INPUT --------
    st.write("### ➕ Add via text")
    c1, c2 = st.columns([3, 1])

    with c1:
        st.text_input(
            "",
            placeholder="fever, headache and dizziness",
            key="typed_text"
        )

    with c2:
        if st.button("Add Text"):
            add_symptoms(split_text(st.session_state.typed_text))
            st.session_state["typed_text"] = ""
            st.rerun()

    # -------- VOICE INPUT --------
    st.divider()
    st.write("### 🎙️ Add via voice")

    audio = audio_recorder("Click to record")

    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio)
            path = f.name

        r = sr.Recognizer()
        try:
            with sr.AudioFile(path) as src:
                data = r.record(src)
            st.session_state["voice_text"] = r.recognize_google(data)
        except:
            st.error("Could not recognize voice")
        finally:
            os.remove(path)

    c3, c4 = st.columns([3, 1])

    with c3:
        st.text_input("Recognized voice", key="voice_text")

    with c4:
        if st.button("Add Voice"):
            add_symptoms(split_text(st.session_state.voice_text))
            st.session_state["voice_text"] = ""
            st.rerun()

# ================= SIDEBAR =================
with side:
    st.write("### 📋 All Added Symptoms")
    if st.session_state.all_symptoms:
        for s in st.session_state.all_symptoms:
            st.success(s)
    else:
        st.info("No symptoms added yet")

# ---------------- SEVERITY ----------------
if not st.session_state.all_symptoms:
    st.warning("Add at least one symptom.")
    st.stop()

severity = "Urgent"
for s in st.session_state.all_symptoms:
    if classify_severity(s) == "Severe":
        severity = "Severe"
        break

def maps_link(level):
    q = "trauma hospital near me" if level == "Severe" else "hospital near me"
    return f"https://www.google.com/maps/search/{q.replace(' ', '+')}"

st.divider()

if severity == "Severe":
    st.error("🔴 SEVERE EMERGENCY")
    st.markdown(f"[🧭 Find Trauma Hospitals]({maps_link(severity)})")
else:
    st.warning("🟠 URGENT MEDICAL ATTENTION NEEDED")
    st.markdown(f"[🧭 Find Nearby Hospitals]({maps_link(severity)})")
