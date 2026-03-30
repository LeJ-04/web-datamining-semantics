import re
import pandas as pd
from difflib import SequenceMatcher
from rdflib import Graph, Namespace, URIRef, OWL, RDF

# Définition des Namespaces utilisés dans le notebook
EX = Namespace("http://www.example.org/football/")
EX_PROP = Namespace(EX + "prop/")
WIKIDATA_NS = Namespace("http://www.wikidata.org/entity/")

def normalize_str(s: str) -> str:
    """
    Normalise une chaîne de caractères (gestion camelCase, underscores, minuscules)
    pour faciliter la comparaison textuelle.
    """
    # Ajoute des espaces entre les majuscules (ex: CamelCase -> Camel Case)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', s)
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
    # Remplace les séparateurs par des espaces
    s1 = s1.replace('_', ' ').replace('-', ' ')
    return " ".join(s1.lower().split())

def similarity_matcher_score(entity_name: str, retrieved_name: str) -> float:
    """
    Calcule un score de confiance entre 0 et 100 basé sur la similarité 
    textuelle de deux noms.
    """
    n1 = normalize_str(entity_name)
    n2 = normalize_str(retrieved_name)
    score = SequenceMatcher(None, n1, n2).ratio() * 100
    return round(score, 2)

def align_entities_from_csv(graph: Graph, mapping_path: str) -> Graph:
    """
    Charge les alignements d'entités depuis le fichier CSV de mapping 
    et les ajoute au graphe via owl:sameAs.
    """
    if not mapping_path:
        return graph

    df = pd.read_csv(mapping_path)
    print(f"Alignement de {len(df)} entités depuis {mapping_path}...")
    
    for _, row in df.iterrows():
        local_uri = URIRef(row["Private Entity"])
        external_uri = URIRef(row["External URI"])
        # Ajout du triplet d'alignement
        graph.add((local_uri, OWL.sameAs, external_uri))
        
    return graph

def align_properties(graph: Graph) -> Graph:
    """
    Définit les équivalences de propriétés entre le schéma local et Wikidata
    tel qu'implémenté dans les étapes finales du notebook.
    """
    # Mapping des propriétés locales vers les IDs Wikidata (P-properties)
    prop_mappings = [
        (EX_PROP.playsFor, "P54"),        # membre de l'équipe
        (EX_PROP.playsPosition, "P413"),  # position de jeu
        (EX_PROP.headCoach, "P286"),      # entraîneur chef
        (EX_PROP.nationality, "P27"),     # citoyenneté
        (EX_PROP.locatedIn, "P17")        # pays
    ]

    for local_prop, wiki_id in prop_mappings:
        wiki_uri = WIKIDATA_NS.term(wiki_id)
        graph.add((local_prop, OWL.equivalentProperty, wiki_uri))
        
    print(f"Alignement de {len(prop_mappings)} propriétés terminé.")
    return graph

def align_entities_and_relations(graph: Graph, mapping_path: str) -> Graph:
    """
    Fonction principale d'orchestration pour l'étape d'alignement.
    """
    # 1. Alignement des instances (Entités) via le CSV
    graph = align_entities_from_csv(graph, mapping_path)
    
    # 2. Alignement du schéma (Propriétés)
    graph = align_properties(graph)
    
    return graph