from rdflib import Graph

g = Graph()
g.parse("data/warehouse.ttl", format="turtle")

PREFIXES = """
PREFIX wh: <http://example.org/warehouse/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

queries = {
    "All facts about product 1": """
        SELECT ?p ?o WHERE { <http://example.org/warehouse/product/1> ?p ?o }
    """,
    "Top 5 suppliers by number of products": """
        SELECT ?supplier (COUNT(?prod) AS ?n)
        WHERE {
            ?prod wh:suppliedBy ?s .
            ?s rdfs:label ?supplier .
        }
        GROUP BY ?supplier
        ORDER BY DESC(?n)
        LIMIT 5
    """,
    "Customers who ordered product 1": """
        SELECT DISTINCT ?name
        WHERE {
            ?o wh:contains <http://example.org/warehouse/product/1> .
            ?o wh:placedBy ?c .
            ?c rdfs:label ?name .
        }
    """,
}

for title, q in queries.items():
    print(f"\n=== {title} ===")
    for row in g.query(PREFIXES + q):
        print(" | ".join(str(x) for x in row))