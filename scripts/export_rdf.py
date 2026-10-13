import os

import psycopg2
from rdflib import Graph, Literal, Namespace, RDF, RDFS

WH = Namespace("http://example.org/warehouse/")

g = Graph()
g.bind("wh", WH)


def node(kind, key):
    """Build a unique URI for an entity, e.g. wh:product/1"""
    return WH[f"{kind}/{key}"]


conn = psycopg2.connect(host="localhost", dbname="warehouse")
cur = conn.cursor()

# Suppliers
cur.execute("SELECT supplier_id, name, country FROM suppliers")
for sid, name, country in cur.fetchall():
    s = node("supplier", sid)
    g.add((s, RDF.type, WH.Supplier))
    g.add((s, RDFS.label, Literal(name)))
    g.add((s, WH.country, Literal(country)))

# Products (the foreign key supplier_id becomes a relationship)
cur.execute("SELECT product_id, name, category, unit_price, supplier_id FROM products")
for pid, name, category, price, sid in cur.fetchall():
    p = node("product", pid)
    g.add((p, RDF.type, WH.Product))
    g.add((p, RDFS.label, Literal(name)))
    g.add((p, WH.category, Literal(category)))
    g.add((p, WH.unitPrice, Literal(price)))
    g.add((p, WH.suppliedBy, node("supplier", sid)))

# Locations
cur.execute("SELECT location_id, warehouse, aisle, bin FROM locations")
for lid, wh, aisle, b in cur.fetchall():
    loc = node("location", lid)
    g.add((loc, RDF.type, WH.Location))
    g.add((loc, RDFS.label, Literal(f"{wh}-{aisle}{b}")))
    g.add((loc, WH.inWarehouse, Literal(wh)))

# Inventory: a relationship that carries a quantity, so it gets its own node
cur.execute("SELECT product_id, location_id, quantity FROM inventory")
for pid, lid, qty in cur.fetchall():
    stock = node("stock", f"{pid}-{lid}")
    g.add((stock, RDF.type, WH.StockEntry))
    g.add((stock, WH.forProduct, node("product", pid)))
    g.add((stock, WH.atLocation, node("location", lid)))
    g.add((stock, WH.quantity, Literal(qty)))
    g.add((node("product", pid), WH.storedAt, node("location", lid)))

# Customers
cur.execute("SELECT customer_id, name, city, country FROM customers")
for cid, name, city, country in cur.fetchall():
    c = node("customer", cid)
    g.add((c, RDF.type, WH.Customer))
    g.add((c, RDFS.label, Literal(name)))
    g.add((c, WH.city, Literal(city)))
    g.add((c, WH.country, Literal(country)))

# Orders
cur.execute("SELECT order_id, customer_id, order_date, promised_date, status FROM orders")
for oid, cid, odate, pdate, status in cur.fetchall():
    o = node("order", oid)
    g.add((o, RDF.type, WH.Order))
    g.add((o, WH.placedBy, node("customer", cid)))
    g.add((o, WH.orderDate, Literal(odate)))
    g.add((o, WH.promisedDate, Literal(pdate)))
    g.add((o, WH.status, Literal(status)))

# Order items: again a relationship with a quantity, so it gets its own node
cur.execute("SELECT order_id, product_id, quantity FROM order_items")
for oid, pid, qty in cur.fetchall():
    item = node("orderitem", f"{oid}-{pid}")
    g.add((item, RDF.type, WH.OrderItem))
    g.add((item, WH.ofOrder, node("order", oid)))
    g.add((item, WH.forProduct, node("product", pid)))
    g.add((item, WH.quantity, Literal(qty)))
    g.add((node("order", oid), WH.contains, node("product", pid)))

# Shipments (delivered_date can be NULL, so only add it when it exists)
cur.execute("SELECT shipment_id, order_id, carrier, shipped_date, delivered_date FROM shipments")
for shid, oid, carrier, shipped, delivered in cur.fetchall():
    sh = node("shipment", shid)
    g.add((sh, RDF.type, WH.Shipment))
    g.add((sh, WH.forOrder, node("order", oid)))
    g.add((sh, WH.carrier, Literal(carrier)))
    if shipped is not None:
        g.add((sh, WH.shippedDate, Literal(shipped)))
    if delivered is not None:
        g.add((sh, WH.deliveredDate, Literal(delivered)))

cur.close()
conn.close()

os.makedirs("data", exist_ok=True)
g.serialize(destination="data/warehouse.ttl", format="turtle")
print(f"Exported {len(g)} triples to data/warehouse.ttl")