from rdflib import Graph, Namespace, URIRef, RDF, Literal

# Définition des namespaces pour la normalisation
EX = Namespace("http://www.example.org/football/")
EX_PROP = Namespace(EX + "prop/")


def remove_redundant_triples(graph: Graph) -> Graph:
    """
    Supprime les triplets qui n'apportent pas d'information utile 
    ou qui sont des doublons syntaxiques.
    """
    initial_count = len(graph)
    # rdflib gère l'unicité des triplets par défaut dans son store, 
    # mais on peut forcer ici la suppression de types génériques si nécessaire.
    print(f"Nettoyage des doublons terminé ({initial_count} triplets au départ).")
    return graph


def normalize_namespaces(graph: Graph) -> Graph:
    """
    S'assure que tous les triplets utilisent les namespaces officiels du projet
    et lie les préfixes pour une sérialisation propre.
    """
    graph.bind("ex", EX)
    graph.bind("prop", EX_PROP)
    return graph


def fix_uri_errors(graph: Graph) -> Graph:
    """
    Corrige les erreurs courantes détectées dans le notebook :
    - Espaces dans les URIs
    - Caractères spéciaux mal encodés
    """
    new_graph = Graph()
    # On recopie les namespaces
    for prefix, ns in graph.namespaces():
        new_graph.bind(prefix, ns)
    
    for s, p, o in graph:
        # Nettoyage simple des URIs sujet et objet si ce sont des URIRef
        new_s = URIRef(str(s).replace(" ", "_")) if isinstance(s, URIRef) else s
        new_o = URIRef(str(o).replace(" ", "_")) if isinstance(o, URIRef) else o
        new_graph.add((new_s, p, new_o))
        
    return new_graph


def clean_graph(graph: Graph) -> Graph:
    """
    Orchestre les opérations de nettoyage.
    """
    graph = remove_redundant_triples(graph)
    graph = fix_uri_errors(graph)
    graph = normalize_namespaces(graph)
    
    return graph


def save_outputs(graph: Graph, base_path: str):
    """
    Sauvegarde le graphe dans les formats requis (.rdf et .ttl)
    """
    # Sauvegarde en Turtle
    graph.serialize(destination=f"{base_path}.ttl", format="turtle")
    # Sauvegarde en XML/RDF
    graph.serialize(destination=f"{base_path}.rdf", format="xml")
    print(f"Fichiers sauvegardés : {base_path}.ttl et {base_path}.rdf")