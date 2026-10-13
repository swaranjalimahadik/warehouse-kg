# Warehouse Knowledge Graph

A personal learning project that models warehouse and logistics data in PostgreSQL
and (in later phases) converts it into a knowledge graph for entity summarization.

## Status
- [x] Phase 1: relational schema, synthetic data generator, views, stored procedure
- [ ] Phase 2: knowledge graph export
- [ ] Phase 3: entity summarization and evaluation (F-Measure, NDCG, MAP)

## Tech stack
Python 3.13, PostgreSQL 18, PL/pgSQL, psycopg2, Faker

## Schema
suppliers, products, locations, inventory, customers, orders, order_items, shipments

## How to run
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
createdb -h localhost warehouse
psql -h localhost -d warehouse -f sql/01_schema.sql
python scripts/generate_data.py
psql -h localhost -d warehouse -f sql/02_views_and_procedures.sql
```

## What I learned
[Two or three sentences in your own words, e.g. about foreign keys, transactions in the procedure, or how this relates to your Oracle work.]