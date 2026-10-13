CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    country     TEXT NOT NULL
);

CREATE TABLE products (
    product_id  SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    unit_price  NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    supplier_id INT NOT NULL REFERENCES suppliers(supplier_id)
);

CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    warehouse   TEXT NOT NULL,
    aisle       TEXT NOT NULL,
    bin         TEXT NOT NULL,
    UNIQUE (warehouse, aisle, bin)
);

CREATE TABLE inventory (
    product_id  INT REFERENCES products(product_id),
    location_id INT REFERENCES locations(location_id),
    quantity    INT NOT NULL CHECK (quantity >= 0),
    PRIMARY KEY (product_id, location_id)
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    city        TEXT NOT NULL,
    country     TEXT NOT NULL
);

CREATE TABLE orders (
    order_id      SERIAL PRIMARY KEY,
    customer_id   INT NOT NULL REFERENCES customers(customer_id),
    order_date    DATE NOT NULL,
    promised_date DATE NOT NULL,
    status        TEXT NOT NULL
                  CHECK (status IN ('NEW','PICKED','SHIPPED','DELIVERED','CANCELLED'))
);

CREATE TABLE order_items (
    order_id   INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity   INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE shipments (
    shipment_id    SERIAL PRIMARY KEY,
    order_id       INT NOT NULL REFERENCES orders(order_id),
    carrier        TEXT NOT NULL,
    shipped_date   DATE,
    delivered_date DATE
);