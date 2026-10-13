import random
from datetime import date, timedelta

import psycopg2
from faker import Faker

random.seed(42)
Faker.seed(42)
fake = Faker()

CATEGORIES = ["Electronics", "Furniture", "Toys", "Clothing", "Tools"]
CARRIERS = ["DHL", "UPS", "FedEx", "DPD"]
STATUSES = ["NEW", "PICKED", "SHIPPED", "DELIVERED", "CANCELLED"]
STATUS_WEIGHTS = [5, 5, 10, 75, 5]

# Postgres.app: no user or password needed, it uses your Mac username
conn = psycopg2.connect(host="localhost", dbname="warehouse")
cur = conn.cursor()

# Start clean so the script can be re-run safely
cur.execute(
    "TRUNCATE shipments, order_items, orders, customers, inventory, "
    "locations, products, suppliers RESTART IDENTITY CASCADE"
)

# Suppliers
for _ in range(20):
    cur.execute(
        "INSERT INTO suppliers (name, country) VALUES (%s, %s)",
        (fake.company(), fake.country()),
    )

# Products
for _ in range(200):
    cur.execute(
        "INSERT INTO products (name, category, unit_price, supplier_id) "
        "VALUES (%s, %s, %s, %s)",
        (fake.catch_phrase(), random.choice(CATEGORIES),
         round(random.uniform(5, 500), 2), random.randint(1, 20)),
    )

# Locations: 2 warehouses x 5 aisles x 10 bins = 100
for wh in ["WH-North", "WH-South"]:
    for aisle in "ABCDE":
        for b in range(1, 11):
            cur.execute(
                "INSERT INTO locations (warehouse, aisle, bin) VALUES (%s, %s, %s)",
                (wh, aisle, f"{b:02d}"),
            )

# Inventory: each product is stored in 1-3 distinct bins
for product_id in range(1, 201):
    for loc_id in random.sample(range(1, 101), random.randint(1, 3)):
        cur.execute(
            "INSERT INTO inventory (product_id, location_id, quantity) "
            "VALUES (%s, %s, %s)",
            (product_id, loc_id, random.randint(0, 120)),
        )

# Customers
for _ in range(100):
    cur.execute(
        "INSERT INTO customers (name, city, country) VALUES (%s, %s, %s)",
        (fake.name(), fake.city(), fake.country()),
    )

# Orders, items, shipments
today = date.today()
for _ in range(1000):
    order_date = today - timedelta(days=random.randint(10, 180))
    promised = order_date + timedelta(days=random.randint(3, 7))
    status = random.choices(STATUSES, STATUS_WEIGHTS)[0]

    cur.execute(
        "INSERT INTO orders (customer_id, order_date, promised_date, status) "
        "VALUES (%s, %s, %s, %s) RETURNING order_id",
        (random.randint(1, 100), order_date, promised, status),
    )
    order_id = cur.fetchone()[0]

    for product_id in random.sample(range(1, 201), random.randint(1, 4)):
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity) "
            "VALUES (%s, %s, %s)",
            (order_id, product_id, random.randint(1, 5)),
        )

    if status in ("SHIPPED", "DELIVERED"):
        shipped = order_date + timedelta(days=random.randint(1, 3))
        delivered = (
            shipped + timedelta(days=random.randint(1, 8))
            if status == "DELIVERED" else None
        )
        cur.execute(
            "INSERT INTO shipments (order_id, carrier, shipped_date, delivered_date) "
            "VALUES (%s, %s, %s, %s)",
            (order_id, random.choice(CARRIERS), shipped, delivered),
        )

conn.commit()
cur.close()
conn.close()
print("Data loaded.")