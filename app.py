import streamlit as st
from emergency_data import classify_severity
from hospitals import get_nearest_hospital

st.set_page_config(page_title="Golden Hour", layout="centered")

st.title("🚨 Golden Hour")
st.subheader("AI Emergency Decision Assistant")
st.write("Instant guidance during trauma emergencies.")
st.divider()

st.write("### What is the emergency?")

emergency = st.radio(
    "",
    [
        "Road Accident",
        "Heavy Bleeding",
        "Burn Injury",
        "Unconscious Person"
    ]
)

severity = classify_severity(emergency)
st.divider()

if severity == "CRITICAL":
    st.error("🔴 CRITICAL EMERGENCY")

    st.write("### Immediate Actions")
    st.write("📞 Call emergency services (108)")
    st.write("🩸 Apply pressure if bleeding")
    st.write("🚑 Move to trauma hospital immediately")

    hospital = get_nearest_hospital(emergency)

    st.divider()
    st.write("### Nearest Trauma Hospital")
    st.write(f"🏥 **{hospital['name']}**")
    st.write(f"📍 Distance: {hospital['distance']}")
    st.markdown(f"[🧭 Navigate]({hospital['maps']})")

else:
    st.warning("🟠 HIGH PRIORITY")
    st.write("Seek medical attention as soon as possible.")

st.divider()

if st.button("🚨 PANIC MODE"):
    st.error("🚨 EMERGENCY MODE ACTIVATED")
    st.markdown("## 📞 CALL AMBULANCE NOW (108)")
    st.markdown("## 🩸 APPLY PRESSURE TO STOP BLEEDING")
    st.markdown("## 🚑 DO NOT DELAY HOSPITAL VISIT")

