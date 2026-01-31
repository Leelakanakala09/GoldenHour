def classify_severity(emergency):
    severe_cases = [
        "Road Accident",
        "Heavy Bleeding",
        "Unconscious Person"
    ]

    if emergency in severe_cases:
        return "Severe"
    else:
        return "Urgent"
