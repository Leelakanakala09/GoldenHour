import streamlit as st
import speech_recognition as sr
import tempfile, os
from audio_recorder_streamlit import audio_recorder
from emergency_data import classify_severity

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Golden Hour", layout="wide")

# ---------------- SESSION STATE ----------------
st.session_state.setdefault("all_options", [
    "Road Accident", "Heavy Bleeding", "Chest Pain",
    "Breathing Problem", "Burn Injury", "Fever",
    "Headache", "Stomach Ache", "Dizziness"
])
st.session_state.setdefault("selected_problems", [])
st.session_state.setdefault("voice_text", "")
st.session_state.setdefault("typed_text", "")

# ---------------- HEADER ----------------
st.title("🚨 Golden Hour")
st.subheader("AI Emergency Decision Assistant")
st.divider()

# ===================== LAYOUT =====================
main_col, side_col = st.columns([3, 1])

# ===================== MAIN COLUMN =====================
with main_col:

    # -------- SELECT PROBLEMS --------
    st.write("### Select all that apply")
    st.multiselect(
        "",
        st.session_state.all_options,
        key="selected_problems"
    )

    # -------- TEXT INPUT --------
    st.write("### ➕ Add your problem")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.session_state.typed_text = st.text_input(
            "",
            placeholder="Example: fever and headache"
        )

    with col2:
        if st.button("Add Text"):
            if st.session_state.typed_text.strip():
                for item in st.session_state.typed_text.replace(",", " and ").split("and"):
                    item = item.strip().title()
                    if item:
                        if item not in st.session_state.all_options:
                            st.session_state.all_options.append(item)
                        if item not in st.session_state.selected_problems:
                            st.session_state.selected_problems.append(item)
                st.session_state.typed_text = ""
                st.rerun()

    # -------- VOICE INPUT --------
    st.divider()
    st.write("### 🎙️ Describe the problem using voice")

    audio_bytes = audio_recorder("Click to record")

    if audio_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_bytes)
            audio_path = f.name

        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
            st.session_state.voice_text = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            st.error("Could not understand the voice input")
        except Exception as e:
            st.error("Voice recognition failed")
        finally:
            os.remove(audio_path)

    # -------- VOICE TEXT BOX --------
    col3, col4 = st.columns([3, 1])

    with col3:
        st.text_input(
            "📝 Recognized Voice Text",
            key="voice_text",
            placeholder="Voice input will appear here"
        )

    with col4:
        if st.button("Add Voice Input"):
            if st.session_state.voice_text.strip():
                for item in st.session_state.voice_text.replace(",", " and ").split("and"):
                    item = item.strip().title()
                    if item:
                        if item not in st.session_state.all_options:
                            st.session_state.all_options.append(item)
                        if item not in st.session_state.selected_problems:
                            st.session_state.selected_problems.append(item)
                st.session_state.voice_text = ""
                st.rerun()

# ===================== SIDEBAR =====================
with side_col:
    st.write("### 📋 Added Symptoms")
    if st.session_state.selected_problems:
        for p in st.session_state.selected_problems:
            st.success(p)
    else:
        st.info("No symptoms added yet")

# ===================== SEVERITY LOGIC =====================
if not st.session_state.selected_problems:
    st.warning("Please add at least one problem to proceed.")
    st.stop()

severity = "Urgent"
for p in st.session_state.selected_problems:
    if classify_severity(p) == "Severe":
        severity = "Severe"
        break

def maps_link(level):
    q = "trauma hospital near me" if level == "Severe" else "hospital near me"
    return f"https://www.google.com/maps/search/{q.replace(' ', '+')}"

st.divider()

# ===================== RESULT =====================
if severity == "Severe":
    st.error("🔴 SEVERE EMERGENCY")
    st.write("📞 Call emergency services immediately")
    st.write("🩸 Provide basic first aid")
    st.markdown(f"[🧭 Find Trauma Hospitals]({maps_link(severity)})")

    if st.button("🚨 PANIC MODE"):
        st.error("CALL AMBULANCE NOW 🚑")

else:
    st.warning("🟠 URGENT MEDICAL ATTENTION NEEDED")
    st.markdown(f"[🧭 Find Nearby Hospitals]({maps_link(severity)})")
