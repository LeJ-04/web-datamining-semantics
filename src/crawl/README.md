# Crawl Module

## Objectif
Collecter des données brutes (textuelles ou structurées) depuis des sources externes.

## Entrées
- URLs ou sources définies dans le code
- Paramètres de crawl

## Sorties
- Fichiers bruts dans `data/` (ex: JSON, CSV, TXT)

## Process
1. Définition des sources
2. Téléchargement des données
3. Nettoyage léger (optionnel)
4. Sauvegarde dans `data/`

## Exemple
```bash
python -m src.crawl.main