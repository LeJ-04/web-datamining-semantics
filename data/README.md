# Part C — Reasoning & Knowledge Graph Embeddings

> **Web Datamining & Semantics Project**
> Knowledge Graph Construction · Alignment · Reasoning & KGE · RAG

---

## 📁 Structure

```
Part C/
├── data/
│   ├── clean_football_kb.ttl         # Graphe RDF nettoyé (input)
│   ├── augmented_football_kb.ttl     # Graphe enrichi après raisonnement SWRL
│   ├── sensitivity_results.json      # Résultats analyse de sensibilité KGE
│   ├── kge_metrics_comparison.csv    # Métriques comparatives TransE vs ComplEx
│   └── kge_metrics_full.csv          # Métriques complètes head/tail/both
├── graphs/
│   ├── kge_training_loss.png         # Courbes de loss TransE et ComplEx
│   ├── kge_sensitivity.png           # Sensibilité à la taille du graphe
│   └── kge_tsne.png                  # Projection t-SNE des embeddings
├── notebooks/
│   └── C_KGE_Reasoning.ipynb         # Notebook principal (C.1 → C.4)
├── kge_dataset/
│   ├── train.txt                     # 58 491 triplets d'entraînement (TSV)
│   ├── valid.txt                     # 3 210 triplets de validation (TSV)
│   └── test.txt                      # 3 209 triplets de test (TSV)
└── models/
    ├── kge_transe/                   # Modèle TransE sauvegardé (PyKEEN)
    │   ├── pipeline_config.json
    │   ├── trained_model.pkl
    │   └── result.json
    └── kge_complex/                  # Modèle ComplEx sauvegardé (PyKEEN)
        ├── pipeline_config.json
        ├── trained_model.pkl
        └── result.json
```

---

## ⚙️ Installation

```bash
pip install rdflib owlready2 pykeen torch scikit-learn matplotlib pandas
```

> **Environnement testé** : Google Colab (GPU T4), Python 3.12
> **Note Java** : Pellet (raisonneur SWRL natif) requiert Java 25+.
> Le notebook utilise SPARQL CONSTRUCT comme alternative sémantiquement équivalente.

---

## 📓 Contenu du notebook

### C.1 — Préparation des données KGE

Chargement du graphe `clean_football_kb.ttl`, filtrage des triplets relationnels (URIs uniquement, pas de littéraux), shuffling et split 80/10/10 avec garantie anti-OOV.

```
Train  : 58 491 triplets
Valid  :  3 210 triplets
Test   :  3 209 triplets
Entités   : 38 655
Relations :    459
```

### C.2 — Raisonnement symbolique SWRL

Déclaration de 2 règles SWRL via `owlready2.Imp` et application via SPARQL CONSTRUCT :

| Règle | Formulation | Triplets inférés |
|---|---|---|
| `coachedBy` | `playsFor(?p,?t) ∧ headCoach(?t,?c) → coachedBy(?p,?c)` | **647** |
| `competesIn` | `playsFor(?p,?t) ∧ locatedIn(?t,?c) → competesIn(?p,?c)` | **647** |

**Graphe final** : 66 996 triplets (+ 1 294 inférés)

### C.3 — Entraînement des modèles KGE

Deux modèles entraînés avec [PyKEEN](https://github.com/pykeen/pykeen) :

| Paramètre | Valeur |
|---|---|
| `embedding_dim` | 128 |
| `epochs` | 200 |
| `batch_size` | 256 |
| `optimizer` | Adam (lr=0.001) |

| Modèle | Loss | Fonction de score |
|---|---|---|
| **TransE** | MarginRankingLoss | h + r ≈ t |
| **ComplEx** | SoftplusLoss | Bilinéaire complexe |

### C.4 — Évaluation, Sensibilité & Visualisation

**Métriques finales (jeu de test complet) :**

| Modèle | MRR | Hits@1 | Hits@3 | Hits@10 | Temps |
|---|---|---|---|---|---|
| **TransE** | **0.1601** | **0.0842** | **0.1783** | **0.3093** | 318s |
| ComplEx | 0.0244 | 0.0099 | 0.0206 | 0.0498 | 604s |

**Sensibilité à la taille :**

| Modèle | 20k MRR | 50k MRR | full MRR |
|---|---|---|---|
| TransE | 0.0678 | 0.1366 | **0.1601** |
| ComplEx | 0.0003 | 0.0095 | **0.0244** |

**Visualisations générées :**
- Courbes de loss (convergence confirmée sur 200 epochs)
- Courbes de sensibilité (progression quasi-linéaire pour TransE)
- Projection t-SNE (38 655 entités → 2D, clusters sémantiques visibles)

**Validation qualitative (plus proches voisins TransE) :**
- Arsenal FC → Leeds United, Man City, Brighton… ✅ clubs Premier League
- England → Sweden, Wales, Norway, Serbia… ✅ pays européens
- Mohamed Salah → Ismaïla Sarr, Lorenzo Lucca… ✅ attaquants internationaux

---

## ▶️ Comment exécuter

### Option A — Google Colab (recommandé)

1. Ouvre `notebooks/C_KGE_Reasoning.ipynb` dans Google Colab
2. Monte ton Google Drive en première cellule
3. Exécute toutes les cellules dans l'ordre (C.1 → C.4)
4. Durée estimée : ~25 min avec GPU T4

### Option B — Après un reset de session Colab

Exécute uniquement la **cellule de secours** (dernière cellule du notebook) pour recharger les modèles sans réentraîner :

```python
from pykeen.pipeline import PipelineResult
result_transe  = PipelineResult.from_directory("models/kge_transe")
result_complex = PipelineResult.from_directory("models/kge_complex")
```

### Option C — Local

```bash
git clone https://github.com/LeJ-04/web-datamining-semantics.git
cd web-datamining-semantics/Part\ C
pip install -r requirements.txt
jupyter notebook notebooks/C_KGE_Reasoning.ipynb
```

---

## 🔑 Points clés & Choix techniques

**Pourquoi SPARQL CONSTRUCT plutôt que Pellet ?**
Pellet (raisonneur SWRL natif d'owlready2) requiert Java 25+. L'environnement Colab dispose de Java 21. SPARQL CONSTRUCT est sémantiquement équivalent — les règles SWRL sont bien déclarées dans l'ontologie via `owlready2.Imp`, seule l'exécution passe par rdflib.

**Pourquoi TransE surpasse ComplEx ?**
Le graphe est très sparse (~1.5 triplets/entité en moyenne) et dominé par une relation asymétrique (`playsFor`). TransE est plus robuste dans ce contexte. ComplEx nécessiterait un tuning dédié (lr plus faible, régularisation L2) pour rivaliser.

**Pourquoi PyKEEN ?**
Librairie de référence pour les KGE en Python, supporte nativement le format TSV, gère automatiquement les entités OOV entre splits, et produit des `PipelineResult` sérialisables pour la persistance.

---

## 📊 Hardware

| Composant | Spec |
|---|---|
| GPU | NVIDIA T4 (Google Colab) |
| RAM | 12 GB |
| Stockage | Google Drive (fichiers lourds exclus du repo) |

> Les fichiers `.xml` (> 6 Mo) et les checkpoints intermédiaires sont exclus du repo via `.gitignore` et disponibles sur Google Drive.
