# Data Directory

## Why is this folder empty?

This folder does not contain static raw data files (like CSVs or JSONs). For this project, data acquisition is handled dynamically using the **football-data.org REST API**. 

We chose this dynamic approach for several reasons:
* **Compliance & Ethics:** The API is a licensed service permitting research usage. By pulling data directly via the API rather than storing static scrapes, we ensure no unauthorized web scraping is performed and rate limits are respected.
* **Freshness:** Fetching data directly guarantees we have the most up-to-date rosters, coaches, and team information.
* **Efficiency:** We gather all necessary information (20 teams, 667 players) using a single authenticated API call.

## Data Source & API Details

* **Source:** [football-data.org API](https://www.football-data.org/)
* **Endpoint Used:** `https://api.football-data.org/v4/competitions/PL/teams` 
* **Domain:** English Premier League (teams, full squads, head coaches, and geographical information).

## Example Data Structure

When the API is called during the `1.kb_modeling.ipynb` notebook execution, it returns a structured JSON. Here is a simplified example of the data payload we extract to build our Knowledge Graph:

```json
{
  "count": 20,
  "competition": {
    "id": 2021,
    "name": "Premier League",
    "code": "PL"
  },
  "teams": [
    {
      "id": 64,
      "name": "Liverpool FC",
      "shortName": "Liverpool",
      "tla": "LIV",
      "area": {
        "id": 2072,
        "name": "England"
      },
      "coach": {
        "id": 11578,
        "name": "Arne Slot",
        "nationality": "Netherlands"
      },
      "squad": [
        {
          "id": 3183,
          "name": "Mohamed Salah",
          "position": "Offence",
          "nationality": "Egypt"
        },
        {
          "id": 1780,
          "name": "Alisson",
          "position": "Goalkeeper",
          "nationality": "Brazil"
        }
      ]
    }
  ]
}
