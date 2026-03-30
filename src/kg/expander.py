import time
from rdflib import Graph, URIRef, Namespace, RDF, OWL
from SPARQLWrapper import SPARQLWrapper, JSON

# Configuration du point d'accès Wikidata
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "FootballKB-Expansion-Bot/1.0"

def get_wiki_expansion_triplets(wiki_ids, limit=200, as_subject=True):
    """
    Récupère les triplets Wikidata pour une liste d'IDs d'entités.
    """
    sparql = SPARQLWrapper(WIKIDATA_ENDPOINT, agent=USER_AGENT)
    
    ids_str = " ".join([f"wd:{wid}" for wid in wiki_ids])
    
    if as_subject:
        query = f"""
        SELECT ?s ?p ?o WHERE {{
            VALUES ?s {{ {ids_str} }}
            ?s ?p ?o .
            FILTER(STRSTARTS(STR(?p), "http://www.wikidata.org/prop/direct/"))
        }} LIMIT {limit}
        """
    else:
        query = f"""
        SELECT ?s ?p ?o WHERE {{
            VALUES ?o {{ {ids_str} }}
            ?s ?p ?o .
            FILTER(STRSTARTS(STR(?p), "http://www.wikidata.org/prop/direct/"))
        }} LIMIT {limit}
        """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        results = sparql.query().convert()
        triplets = []
        for result in results["results"]["bindings"]:
            triplets.append((
                result["s"]["value"],
                result["p"]["value"],
                result["o"]["value"]
            ))
        return triplets
    except Exception as e:
        print(f"Erreur lors de la requête SPARQL: {e}")
        return []

def extend_graph(graph, triplets):
    """
    Ajoute les triplets extraits au graphe RDFlib.
    """
    for s, p, o in triplets:
        # On ne garde que les URIs pour la consistance du graphe
        if s.startswith("http") and p.startswith("http") and o.startswith("http"):
            graph.add((URIRef(s), URIRef(p), URIRef(o)))
    return graph

def expand_graph(graph, batch_size=20, limit_per_batch=200):
    """
    Orchestre l'expansion du graphe pour toutes les entités ayant un owl:sameAs.
    """
    print("Démarrage de l'expansion du graphe via Wikidata...")
    
    # 1. Identifier les entités alignées (qui ont un lien Wikidata)
    query_aligned = """
    SELECT ?wiki_uri WHERE {
        ?s <http://www.w3.org/2002/07/owl#sameAs> ?wiki_uri .
        FILTER(STRSTARTS(STR(?wiki_uri), "http://www.wikidata.org/entity/"))
    }
    """
    wiki_uris = [str(r[0]) for r in graph.query(query_aligned)]
    wiki_ids = [uri.split("/")[-1] for uri in wiki_uris]
    
    if not wiki_ids:
        print("Aucune entité alignée trouvée pour l'expansion.")
        return graph

    print(f"Expansion pour {len(wiki_ids)} entités par batch de {batch_size}...")
    
    expansion_triplets = []
    for i in range(0, len(wiki_ids), batch_size):
        batch = wiki_ids[i:i+batch_size]
        print(f"Traitement du batch {i//batch_size + 1}...", end="\r")
        
        # Récupération des triplets (Step 1-hop)
        triplets = get_wiki_expansion_triplets(batch, limit=limit_per_batch)
        expansion_triplets.extend(triplets)
        
        # Petit délai pour respecter les limites de l'API Wikidata
        time.sleep(0.5)

    # 2. Intégration des nouveaux triplets
    graph = extend_graph(graph, expansion_triplets)
    print(f"\nExpansion terminée : {len(expansion_triplets)} triplets ajoutés.")
    
    return graph