from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

def extract_triplets(data):
    """
    Extraction des triplets (s, p, o).
    """
    g = Graph()

    EX = Namespace("http://www.example.org/football/")
    g.bind("ex", EX)

    EX_PROP = Namespace(EX + "prop/")
    g.bind("prop", EX_PROP)

    teams = data["teams"]
    for t in teams:

        team_uri = URIRef(EX + t["name"].replace(" ", "_"))
        g.add((team_uri, RDF.type, EX.Team))

        # Team's country
        team_country_uri = URIRef(EX + t["area"]["name"].replace(" ", "_"))
        g.add((team_country_uri, RDF.type, EX.Country))
        g.add((team_uri, EX_PROP.locatedIn, team_country_uri))


        # Team's coach
        coach_uri = URIRef(EX + t["coach"]["name"].replace(" ", "_"))
        g.add((coach_uri, RDF.type, EX.Person))
        g.add((team_uri, EX_PROP.headCoach, coach_uri))


        # Team's coach nationality
        coach_country_uri = URIRef(EX + t["coach"]["nationality"].replace(" ", "_"))
        g.add((coach_country_uri, RDF.type, EX.Country))
        g.add((coach_uri, EX_PROP.nationality, coach_country_uri))

        for player in t["squad"]:
            # Player of a team
            player_uri = URIRef(EX + player["name"].replace(" ", "_"))
            g.add((player_uri, RDF.type, EX.Person))
            g.add((player_uri, EX_PROP.playsFor, team_uri))


            # Player's nationality
            player_country_uri = URIRef(EX + player["nationality"].replace(" ", "_"))
            g.add((player_country_uri, RDF.type, EX.Country))
            g.add((player_uri, EX_PROP.nationality, player_country_uri))


            # Player's Position
            if player["position"]:
                position_uri = URIRef(EX + player["position"].replace(" ", "_"))
                g.add((position_uri, RDF.type, EX.FootballPosition))
                g.add((player_uri, EX_PROP.playsPosition, position_uri))
    return g