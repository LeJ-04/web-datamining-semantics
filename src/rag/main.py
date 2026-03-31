import os
import re
import time
import shutil
import rdflib
from rdflib import RDF, Namespace
from groq import Groq
import pandas as pd

# --- CONFIGURATION ---
# Remplacez par votre clé si vous n'êtes pas sur Colab
# os.environ["GROQ_API_KEY"] = "votre_cle_ici"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") 
GROQ_MODEL = "llama-3.3-70b-versatile"
TTL_FILE_PATH = "augmented_football_kb.ttl" # Assurez-vous que le fichier est dans le même dossier

if not GROQ_API_KEY:
    raise ValueError("La clé API GROQ_API_KEY est manquante dans les variables d'environnement.")

# Initialisation du client Groq
client = Groq(api_key=GROQ_API_KEY)

# --- LOGIQUE DU GRAPH ---
g = rdflib.Graph()
EX = Namespace("http://www.example.org/football/")
EX_PROP = Namespace("http://www.example.org/football/prop/")

def load_knowledge_graph(path):
    if not os.path.exists(path):
        print(f"⚠️ Erreur : Le fichier {path} est introuvable.")
        return False
    print(f"⏳ Chargement du Knowledge Graph ({path})...")
    g.parse(path, format="turtle")
    print(f"✅ Graph chargé : {len(g):,} triplets.")
    return True

# --- FONCTIONS LLM & SPARQL ---

def llm_generate(prompt: str) -> str:
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()

def clean_sparql(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"```sparql\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)
    return raw.strip()

def execute_sparql(query: str):
    try:
        results = g.query(query)
        rows = []
        for row in results:
            rows.append({
                str(var): str(val)
                .replace("http://www.example.org/football/", "")
                .replace("http://www.example.org/football/prop/", "prop:")
                .replace("_", " ")
                for var, val in zip(results.vars, row)
            })
        return rows, None
    except Exception as e:
        return None, str(e)

# --- LOGIQUE DE RÉPARATION & GÉNÉRATION ---

def get_schema_summary():
    # Simplification pour le prompt (basé sur votre logique initiale)
    return """
BASE NAMESPACES:
  Entities   : http://www.example.org/football/
  Properties : http://www.example.org/football/prop/
SPARQL PREFIXES:
  PREFIX ex:   <http://www.example.org/football/>
  PREFIX prop: <http://www.example.org/football/prop/>
  PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
RULES:
  1. URIs avec underscores (ex: Arsenal_FC). 2. Toujours filtrer par rdf:type ex:Person ou ex:Team.
  3. Propriétés dans prop/ (ex: prop:playsFor). 4. Utiliser STR() et LCASE() pour FILTER CONTAINS.
"""

def process_question(question: str):
    schema = get_schema_summary()
    
    # 1. Génération
    prompt = f"Generate ONE raw SPARQL SELECT query for: {question}\n\nSchema:\n{schema}\n\nSPARQL QUERY:"
    query = clean_sparql(llm_generate(prompt))
    
    # 2. Exécution & Auto-réparation (1 tentative simplifiée ici)
    results, error = execute_sparql(query)
    
    if error or not results:
        repair_prompt = f"Fix this SPARQL query. Error: {error if error else 'No results'}\nQuery: {query}\n\nFixed SPARQL:"
        query = clean_sparql(llm_generate(repair_prompt))
        results, error = execute_sparql(query)
    
    return query, results, error

# --- INTERFACE CLI ---

def display_table(results):
    if not results:
        print("\n   [!] Aucun résultat trouvé.")
        return
    
    df = pd.DataFrame(results)
    print("\n" + "="*30)
    print(df.to_string(index=False))
    print("="*30)
    print(f"Total : {len(results)} résultat(s)")

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        FOOTBALL KNOWLEDGE GRAPH - CHAT INTERFACE         ║")
    print("╚══════════════════════════════════════════════════════════╝")

    if not load_knowledge_graph(TTL_FILE_PATH):
        return

    print("\n💡 Exemples : ")
    print(" - Which players play for Arsenal FC?")
    print(" - Who is the head coach of Liverpool FC?")
    print(" - How many teams are in England?")

    while True:
        try:
            user_input = input("\n🎯 Posez votre question (ou 'exit') : ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("👋 Au revoir !")
                break
            
            if not user_input:
                continue

            print("🔍 Analyse en cours...")
            query, results, error = process_question(user_input)

            if error:
                print(f"❌ Erreur lors de l'exécution : {error}")
            else:
                print(f"🤖 SPARQL généré :\n{query}")
                display_table(results)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"💥 Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    main()