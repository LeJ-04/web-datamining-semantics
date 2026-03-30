from .crawler import crawl_sources
from .utils import save_raw_data


def run():
    data = crawl_sources()
    save_raw_data(data, output_path="data/raw_data.json")


if __name__ == "__main__":
    run()