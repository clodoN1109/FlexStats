import json
import random
from pathlib import Path

def main():
    # Directory of this script
    script_dir = Path(__file__).resolve().parent
    file_path = script_dir / "test-event.json"

    # Fixed properties
    properties = {
        "temperature": random.uniform(15.0, 30.0),  # float
        "humidity": random.randint(20, 90),         # int
        "status": random.choice(["ok", "warning", "critical"]),  # string
    }

    # If file exists, just overwrite with new random values
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(properties, f, indent=4)

    print(f"Updated {file_path} with new random values.")

if __name__ == "__main__":
    main()
