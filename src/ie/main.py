from .preprocessing import preprocess
from .extractor import extract_triplets
import json


INPUT_FILE = "data/raw_data.json"
OUTPUT_FILE = "artifacts/football_kb.ttl"


def run():
    with open(INPUT_FILE) as f:
        raw_data = json.load(f)

    processed = preprocess(raw_data)
    g = extract_triplets(processed)

    g.serialize(OUTPUT_FILE, format="turtle")


if __name__ == "__main__":
    run()