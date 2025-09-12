import json
import random

def generate_event():
    """
    Generates a random event dictionary with temperature, humidity, and status.
    Returns:
        dict: The event data.
    """
    properties = {
        "temperature": random.uniform(15.0, 30.0),  # float
        "humidity": random.randint(20, 90),         # int
        "status": random.choice(["ok", "warning", "critical"]),  # string
    }
    return properties

def main():
    event_data = generate_event()
    print(json.dumps(event_data, indent=4))  # Optional: print as JSON string
    return event_data

if __name__ == "__main__":
    main()