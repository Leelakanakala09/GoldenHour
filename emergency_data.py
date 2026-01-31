def classify_severity(emergency):
    severe = [
        "Road Accident",
        "Heavy Bleeding",
        "Chest Pain",
        "Breathing Problem"
    ]

    urgent = [
        "Burn Injury"
    ]

    if emergency in severe:
        return "Severe"
    elif emergency in urgent:
        return "Urgent"
    else:
        return "Urgent"
