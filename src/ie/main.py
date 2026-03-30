from .preprocessing import preprocess
from .extractor import extract_triplets
import json


INPUT_FILE = "data/raw_data.json"


def run():
    with open(INPUT_FILE) as f:
        raw_data = json.load(f)

    processed = preprocess(raw_data)
    g = extract_triplets(processed)
    triplets = list(g)

    with open("artifacts/extracted_triplets.json", "w") as f:
        json.dump(triplets, f, indent=2)


if __name__ == "__main__":
    run()