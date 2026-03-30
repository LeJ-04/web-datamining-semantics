# Knowledge Graph (KG)

## Objectif
Construire, nettoyer, enrichir et aligner un graphe de connaissances RDF à partir de triplets extraits.

Ce module correspond directement au notebook `kb_modeling.ipynb`.

---

## Entrées

- `artifacts/football_kb.ttl`

---

## Sorties

Les fichiers produits correspondent à ceux déjà présents dans le repo :

- `artifacts/football_kb.ttl` → graphe brut
- `artifacts/ent_aligned_football_kb.ttl` → alignement entités
- `artifacts/aligned_football_kb.ttl` → graphe aligné
- `artifacts/expanded_football_kb.ttl` → graphe enrichi
- `artifacts/clean_football_kb.ttl` → graphe nettoyé

---

## Process

### 1. Construction du graphe RDF
- Conversion des triplets (head, relation, tail)
- Utilisation de `rdflib`
- Création du graphe initial `football_kb.rdf`

---

### 2. Alignement (schema & entités)
- Mapping entre différentes représentations (avec wikidata)
- Utilisation de tables d’alignement :
  - `alignement_mapping_table.csv`
- Alignement :
  - des entités
  - des relations

→ Outputs :
- `ent_aligned_football_kb.rdf`
- `aligned_football_kb.rdf`

---

### 3. Enrichissement / Expansion
- Ajout de nouvelles relations
- Expansion 1-hop
- Expansion 2-hop
- Augmentation du graphe existant

→ Outputs :
- `expanded_football_kb.ttl`

---

### 4. Nettoyage du graphe
- Suppression des doublons
- Normalisation des URI
- Vérification du namespace
- Correction de relations inconsistantes

→ Output : `clean_football_kb.rdf` + `.ttl`

---

## Exemple

```bash
python -m src.kg.main