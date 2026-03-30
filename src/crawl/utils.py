import json


def save_raw_data(data, output_path):
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)