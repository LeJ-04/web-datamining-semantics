import os
import requests

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

def crawl_sources():
    """
    Point central de collecte des données.
    """
    url = "https://api.football-data.org/v4/competitions/PL/teams"
    headers = {"X-Auth-Token": API_KEY}

    response = requests.get(url, headers=headers)
    data = response.json()
    return data