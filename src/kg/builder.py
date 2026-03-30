from rdflib import Graph, Namespace, URIRef, RDF

EX = Namespace("http://www.example.org/football/")
EX_PROP = Namespace(EX + "prop/")

def build_rdf_graph(input_path: str) -> Graph:
    """
    Charge le graphe initial et s'assure que les namespaces sont liés.
    """
    g = Graph()
    g.parse(input_path, format="turtle")
    g.bind("ex", EX)
    g.bind("prop", EX_PROP)
    return g


def get_graph_stats(graph):
    """
    Calcule les statistiques du graphe via SPARQL.
    """
    graph_stats = dict()
    graph_stats["num_triples"] = len(graph)

    triplets_stats_query = """
    SELECT (COUNT(DISTINCT ?s) AS ?num_subjects) (COUNT(DISTINCT ?p) AS ?num_predicates) (COUNT(DISTINCT ?o) AS ?num_objects)
    WHERE {
        ?s ?p ?o
    }
    """.strip()
    triplets_stats_query_result = next(iter(graph.query(triplets_stats_query)))
    graph_stats["num_subjects"] = triplets_stats_query_result.num_subjects
    graph_stats["num_objects"] = triplets_stats_query_result.num_objects
    graph_stats["num_predicates"] = triplets_stats_query_result.num_predicates

    num_entities_query = """
    SELECT (COUNT(DISTINCT ?entity) AS ?num)
    WHERE {
        {
            ?entity ?p ?o .
            FILTER(isIRI(?entity))
        }
        UNION
        {
            ?s ?p ?entity .
            FILTER(isIRI(?entity))
        }
    }
    """.strip()
    graph_stats["num_entities"] = next(iter(graph.query(num_entities_query))).num

    return graph_stats


def display_graph_stats(graph):
    graph_stats = get_graph_stats(graph)

    for k, v in graph_stats.items():
        var_name = k.split("_")[-1]
        if k.startswith("num_"):
            print(f"Number of {var_name}: {v}")
