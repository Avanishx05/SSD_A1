# GigTask Database Setup

## Prerequisites
- PostgreSQL 16+ and MongoDB installed and running locally
- Python 3 with dependencies from data_generation/requirements.txt

## Setup order (Postgres)
1. createdb gigtask_db
2. Run SQL files in order:
   - psql gigtask_db -f sql/01_schema_ddl.sql
   - psql gigtask_db -f sql/02_indexes.sql
   - psql gigtask_db -f sql/03_triggers_and_audit.sql
   - psql gigtask_db -f sql/04_stored_procedures.sql
   - psql gigtask_db -f sql/05_materialized_views.sql
3. Seed data: python3 data_generation/postgres_seeder.py
4. After seeding, sync identity sequences to the seeder's manually-assigned IDs:
   - SELECT setval(pg_get_serial_sequence('clients', 'id'), (SELECT MAX(id) FROM clients));
   - SELECT setval(pg_get_serial_sequence('freelancers', 'id'), (SELECT MAX(id) FROM freelancers));
   - SELECT setval(pg_get_serial_sequence('contracts', 'id'), (SELECT MAX(id) FROM contracts));
   - SELECT setval(pg_get_serial_sequence('wallet_audit_logs', 'id'), (SELECT MAX(id) FROM wallet_audit_logs));

## Setup order (MongoDB)
1. mongosh gigtask_db mongo/01_collections_and_indexes.js
2. Seed data: python3 data_generation/mongo_seeder.py
3. Run workflow scripts: mongo/02_workflow3_geonear.js, mongo/03_workflow4_facet.js

## Known behavior: WorkerLocations TTL vs. bulk seeding
WorkerLocations has a 2-hour TTL index (per spec, modeling live location pings).
Seeded documents are timestamped 0-5 minutes in the past to simulate "just pinged"
workers, giving the full batch a safe ~2-hour runway before any natural expiry.
Performance captures for Workflow 3 ($geoNear) were taken shortly after seeding.

## Data scale (verified)
- wallet_audit_logs: 150,000+ rows
- contracts: 60,000+ rows
- WorkerLocations: 600,000 documents

## PostgreSQL Business Logic

### Escrow Audit Logging
- `sql/03_triggers_and_audit.sql`
- `AFTER UPDATE` trigger on `clients.escrow_balance`
- Automatically records escrow balance changes in `wallet_audit_logs`
- Records client ID, amount changed, action type, balance after, and timestamp

### Atomic Gig Funding
- `sql/04_stored_procedures.sql`
- Implements the `fund_gig()` stored procedure
- Validates gig budget, client, and freelancer
- Locks the client row using `FOR UPDATE`
- Adds the gig budget to the client's escrow balance
- Creates a `FUNDED` contract
- Escrow update and contract creation execute atomically

### Freelancer Lifetime Earnings
- `sql/05_materialized_views.sql`
- Materialized view: `freelancer_lifetime_earnings`
- Stores lifetime completed contract count and total completed earnings
- Unique index on `freelancer_id` supports concurrent refresh
- Refresh using:
  - `REFRESH MATERIALIZED VIEW CONCURRENTLY freelancer_lifetime_earnings;`

## PostgreSQL Performance Proof

### Window Analytics
- `EXPLAIN ANALYZE` confirms use of the `idx_completed_gig` index
- Index used:
  - `Index Scan using idx_completed_gig on contracts`
- Completed contract rows processed: 41,452
- Execution time: 97.555 ms

### Partial Index Verification
- `EXPLAIN ANALYZE` confirms use of the `idx_active_gig` partial index
- Index used:
  - `Index Scan using idx_active_gig on contracts`
- Index condition: `freelancer_id = 1`
- Execution time: 0.577 ms

Complete PostgreSQL execution plans are available in:
- `performance/postgres_explain_analyzes.txt`
with an execution time of approximately 0.577 ms.
