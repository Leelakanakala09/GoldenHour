def get_nearby_hospitals(emergency):
    if emergency in ["Road Accident", "Heavy Bleeding", "Chest Pain", "Breathing Problem"]:
        query = "trauma hospital near me"
    else:
        query = "hospital near me"

    maps_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

    return {
        "maps": maps_url
    }
