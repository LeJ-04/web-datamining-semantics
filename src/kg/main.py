import os
from src.kg.builder import build_rdf_graph, get_graph_stats
from src.kg.aligner import align_entities_and_relations
from src.kg.expander import expand_graph
from src.kg.cleaner import clean_graph, save_graph

def main():
    # Chemins des fichiers
    IN_RAW = "artifacts/football_kb.ttl"
    IN_MAPPING = "artifacts/alignement_mapping_table.csv"
    OUT_CLEAN = "artifacts/clean_football_kb.ttl"
    
    # 1. Construction / Load
    g = build_rdf_graph(IN_RAW)
    print("Stats initiales:", get_graph_stats(g))
    
    # 2. Alignement
    g = align_entities_and_relations(g, IN_MAPPING)
    
    # 3. Expansion (Optionnel selon le process)
    g = expand_graph(g)
    
    # 4. Nettoyage et Sauvegarde
    g = clean_graph(g)
    save_graph(g, OUT_CLEAN)

if __name__ == "__main__":
    main()