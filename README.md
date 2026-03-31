# Web Datamining & Semantics: Premier League Knowledge Graph  

## Project Overview  

This project implements a complete Neuro-Symbolic pipeline focusing on the English Premier League football domain. It integrates Knowledge Graph (KG) construction, ontology alignment, symbolic SWRL reasoning, Knowledge Graph Embeddings (KGE), and Retrieval-Augmented Generation (RAG) over RDF/SPARQL.  

**Authors:** BACHABI Rochdy & SAINT ANDRE Jeffrey (ESILV A4 DIA, Semester 2 March 2026)  

## Demo Video & Visuals
* **Watch the RAG Demo:** [Youtube Demo Video !](https://youtu.be/gGVF1trnNGU) 

## Repository Structure  
Based on the grading guidelines and project structure, the repository is organized as follows:  

* **`src/`**: Source code modules  
    * `crawl/`: Data collection using a single authenticated API call to the football-data.org REST API  
    * `ie/`: Information extraction, cleaning pipeline, and entity normalization  
    * `kg/`: RDF modeling choices, alignment functions, and SPARQL utilities  
* **`notebooks/`**: Main pipeline execution  
    * `1.kb_modeling.ipynb`: Covers KB construction via RDFLib, Wikidata alignment via SequenceMatcher, and SPARQL CONSTRUCT expansion  
    * `2.resoning_kge.ipynb`: Applies SWRL reasoning rules (`coachedBy`, `competesin`) and trains KGE models using PyKEEN  
    * `3.rag.ipynb`: Implements the NL-to-SPARQL RAG pipeline with Groq Llama-3.3-70b and the self-repair mechanism  
* **`artifacts/`**: Generated Knowledge Graph artifacts
    * Contains initial `.rdf`, `.ttl` files, and the `kge_dataset/` split (`train.txt`, `valid.txt`, `test.txt`)  
* **`eval/`**: Evaluation artifacts
    * Contains metrics `.csv` files and visualizations (like t-SNE `.png` outputs).
* **`model/`**: Saved models
    * Contains PyKEEN trained embeddings (`kge_transE`, `kge_complEx`, `kge_distMult`).

## Hardware Requirements
* **KGE Training:** A GPU is strongly recommended. The KGE models (TransE, ComplEx, DistMult) were trained using a Google Colab T4 GPU.
* **Reasoning Tools:** Native SWRL reasoners (like Pellet) require Java 25+. To bypass Colab constraints (Java 21), SPARQL CONSTRUCT is used as a semantic equivalent.
* **RAG API:** An active internet connection is required to connect to the Groq API (LLaMA-3.3-70b).

## Installation
1. Clone this repository to your local machine.
2. Install the required dependencies:  
   ```bash
   pip install -r requirements.txt
