# Information Extraction (IE)

## Objectif
Extraire des entités et relations à partir des données brutes.

## Entrées
- Données brutes depuis `data/`

## Sorties
- Triplets (head, relation, tail)
- Fichiers intermédiaires (CSV/JSON)

## Process
1. Préprocessing du texte
2. Extraction d'entités
3. Extraction de relations
4. Structuration en triplets

## Exemple
```bash
python -m src.ie.main