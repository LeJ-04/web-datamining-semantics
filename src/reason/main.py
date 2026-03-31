import os
import rdflib
from rdflib import RDF, OWL, Namespace, URIRef
from rdflib.namespace import RDFS

from owlready2 import World, Thing, ObjectProperty, Imp

g = rdflib.Graph()
g.parse("clean_football_kb.ttl", format="turtle")

ONTO_IRI = "http://www.example.org/football/"
EX       = Namespace(ONTO_IRI)       # entités
EX_PROP  = Namespace(EX + "prop/")  # propriétés

g.add((URIRef(ONTO_IRI), RDF.type, OWL.Ontology))


for cls in ["Person", "Team", "Country", "FootballPosition"]:
    g.add((EX[cls], RDF.type, OWL.Class))

# Declaration of properties (existing + inferred)
for p in ["playsFor", "headCoach", "locatedIn",
          "nationality", "playsPosition", "coachedBy", "competesIn"]:
    g.add((EX_PROP[p], RDF.type, OWL.ObjectProperty))


g.add((EX_PROP["coachedBy"],  RDFS.domain, EX["Person"]))
g.add((EX_PROP["coachedBy"],  RDFS.range,  EX["Person"]))
g.add((EX_PROP["competesIn"], RDFS.domain, EX["Person"]))
g.add((EX_PROP["competesIn"], RDFS.range,  EX["Country"]))


IGNORE = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty,
          OWL.AnnotationProperty, OWL.Ontology, OWL.NamedIndividual}
for s, p, o in list(g.triples((None, RDF.type, None))):
    if o not in IGNORE and isinstance(s, URIRef):
        g.add((s, RDF.type, OWL.NamedIndividual))

count_ni = len(list(g.triples((None, RDF.type, OWL.NamedIndividual))))
print(f"   -> {count_ni} entities NamedIndividual")


for prop in ["playsFor", "locatedIn", "headCoach"]:
    triples = list(g.triples((None, EX_PROP[prop], None)))
    ex = triples[0] if triples else None
    print(f"   -> '{prop}' : {len(triples)} triplets" +
          (f"  (ex: {ex[0].split('/')[-1]} → {ex[2].split('/')[-1]})" if ex else "Nothing"))


xml_file = os.path.abspath("clean_football_kb_typed.xml")
g.serialize(xml_file, format="xml")
print(f"   -> XML file: {xml_file}")

my_world = World()
onto     = my_world.get_ontology(f"file://{xml_file}/").load()

Person  = onto.search_one(iri=str(EX["Person"]))
Team    = onto.search_one(iri=str(EX["Team"]))
Country = onto.search_one(iri=str(EX["Country"]))

if not all([Person, Team, Country]):
    print("Classes not found :")
    for i, e in enumerate(list(onto.individuals())[:5]):
        print(f"     {e.iri}")
    raise RuntimeError("Check EX and EX_PROP namespaces")

print(f"   -> Person={Person.name} | Team={Team.name} | Country={Country.name}")

prop_ns = my_world.get_namespace(str(EX_PROP))


with onto:
    # Rules 1
    rule1 = Imp()
    rule1.set_as_rule(
        "Person(?p), Team(?t), Person(?c), "
        "playsFor(?p, ?t), headCoach(?t, ?c) -> coachedBy(?p, ?c)",
        namespaces=[onto, prop_ns]
    )
    # Rules 2
    rule2 = Imp()
    rule2.set_as_rule(
        "Person(?p), Team(?t), Country(?c), "
        "playsFor(?p, ?t), locatedIn(?t, ?c) -> competesIn(?p, ?c)",
        namespaces=[onto, prop_ns]
    )

print("-> Rules 1 : Person(?p) ∧ Team(?t) ∧ Person(?c)  ∧ playsFor(?p,?t) ∧ headCoach(?t,?c) → coachedBy(?p,?c)")
print("-> Rules 2 : Person(?p) ∧ Team(?t) ∧ Country(?c) ∧ playsFor(?p,?t) ∧ locatedIn(?t,?c) → competesIn(?p,?c)")

g.bind("ex",   EX)
g.bind("prop", EX_PROP)
g.bind("owl",  OWL)

SPARQL_RULE1 = """
PREFIX ex:   <http://www.example.org/football/>
PREFIX prop: <http://www.example.org/football/prop/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
CONSTRUCT { ?p prop:coachedBy ?c . }
WHERE {
    ?p  rdf:type       ex:Person .
    ?t  rdf:type       ex:Team   .
    ?c  rdf:type       ex:Person .
    ?p  prop:playsFor  ?t .
    ?t  prop:headCoach ?c .
}
"""

SPARQL_RULE2 = """
PREFIX ex:   <http://www.example.org/football/>
PREFIX prop: <http://www.example.org/football/prop/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
CONSTRUCT { ?p prop:competesIn ?c . }
WHERE {
    ?p  rdf:type        ex:Person  .
    ?t  rdf:type        ex:Team    .
    ?c  rdf:type        ex:Country .
    ?p  prop:playsFor   ?t .
    ?t  prop:locatedIn  ?c .
}
"""

new_triples_1 = list(g.query(SPARQL_RULE1))
for triple in new_triples_1:
    g.add(triple)
count_coached = len(new_triples_1)

new_triples_2 = list(g.query(SPARQL_RULE2))
for triple in new_triples_2:
    g.add(triple)
count_competes = len(new_triples_2)

print(f"Rules 1 (coachedBy)  -> {count_coached}  new triplets")
print(f"Rules 2 (competesIn) -> {count_competes} new triplets")

print("\nExample : competesIn")
q_ex_competes = """
PREFIX prop: <http://www.example.org/football/prop/>
SELECT ?player ?country WHERE { ?player prop:competesIn ?country . } LIMIT 5
"""
for row in g.query(q_ex_competes):
    player  = str(row.player).split('/')[-1]
    country = str(row.country).split('/')[-1]
    print(f"     {player} compète en {country}")

print("\nExample : coachedBy")
q_ex_coached = """
PREFIX prop: <http://www.example.org/football/prop/>
SELECT ?player ?coach WHERE { ?player prop:coachedBy ?coach . } LIMIT 5
"""
for row in g.query(q_ex_coached):
    player = str(row.player).split('/')[-1]
    coach  = str(row.coach).split('/')[-1]
    print(f"     {player} est coaché par {coach}")

print("\nTop 5 players by competition country")
q_by_country = """
PREFIX prop: <http://www.example.org/football/prop/>
SELECT ?country (COUNT(?player) AS ?nb)
WHERE { ?player prop:competesIn ?country . }
GROUP BY ?country ORDER BY DESC(?nb) LIMIT 5
"""
for row in g.query(q_by_country):
    country = str(row.country).split('/')[-1]
    print(f"     {country} : {int(row.nb)} joueurs")

augmented_ttl = "augmented_football_kb.ttl"
augmented_xml = "augmented_football_kb.xml"

g.serialize(augmented_ttl, format="turtle")
onto.save(file=augmented_xml, format="rdfxml")

total_triples = len(list(g.triples((None, None, None))))

print(f"Total final triples:, {total_triples}")