def classify_severity(emergency):
    critical_cases = [
        "Road Accident",
        "Heavy Bleeding",
        "Unconscious Person"
    ]

    if emergency in critical_cases:
        return "CRITICAL"
    else:
        return "HIGH"
