import argparse
import random
import uuid
from decimal import Decimal

import psycopg2
from faker import Faker


fake = Faker()


# --------------------------------------------------
# Configuration
# --------------------------------------------------

DEFAULT_CLIENTS = 10_000
DEFAULT_FREELANCERS = 5_000
DEFAULT_CONTRACTS = 60_000
DEFAULT_AUDITS = 150_000


# --------------------------------------------------
# Database connection
# --------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="gigtask",
        user="postgres",
        password="YOUR_POSTGRES_PASSWORD"
    )


# --------------------------------------------------
# Generate clients
# --------------------------------------------------

def generate_clients(count):
    clients = []

    for _ in range(count):
        clients.append((
            str(uuid.uuid4()),
            fake.name(),
            Decimal(str(round(random.uniform(500, 50000), 2)))
        ))

    return clients


# --------------------------------------------------
# Generate freelancers
# --------------------------------------------------

def generate_freelancers(count):
    freelancers = []

    cities = [
        (13.0827, 80.2707),   # Chennai
        (12.9716, 77.5946),   # Bengaluru
        (17.3850, 78.4867),   # Hyderabad
        (19.0760, 72.8777),   # Mumbai
        (28.6139, 77.2090),   # Delhi
    ]

    for _ in range(count):

        base_lat, base_lon = random.choice(cities)

        # Small geographic variation around the city
        latitude = base_lat + random.uniform(-0.15, 0.15)
        longitude = base_lon + random.uniform(-0.15, 0.15)

        freelancers.append((
            str(uuid.uuid4()),
            fake.name(),
            latitude,
            longitude,
            random.choice([True, True, True, False])
        ))

    return freelancers


# --------------------------------------------------
# Generate contracts
# --------------------------------------------------

def generate_contracts(count, clients, freelancers):

    contracts = []

    client_ids = [c[0] for c in clients]
    freelancer_ids = [f[0] for f in freelancers]

    statuses = [
        "FUNDED",
        "IN_PROGRESS",
        "COMPLETED"
    ]

    for _ in range(count):

        contracts.append((
            str(uuid.uuid4()),
            random.choice(client_ids),
            random.choice(freelancer_ids),
            round(random.uniform(100, 10000), 2),
            random.choices(
                statuses,
                weights=[20, 20, 60],
                k=1
            )[0],
            fake.date_time_between(
                start_date="-2 years",
                end_date="now"
            )
        ))

    return contracts


# --------------------------------------------------
# Generate audit logs
# --------------------------------------------------

def generate_audit_logs(count, clients):

    logs = []

    client_ids = [c[0] for c in clients]

    for _ in range(count):

        amount = round(random.uniform(-1000, 5000), 2)

        logs.append((
            str(uuid.uuid4()),
            random.choice(client_ids),
            amount,
            random.choice([
                "DEPOSIT",
                "WITHDRAWAL",
                "CONTRACT_FUND",
                "REFUND"
            ]),
            round(random.uniform(0, 50000), 2),
            fake.date_time_between(
                start_date="-2 years",
                end_date="now"
            )
        ))

    return logs


# --------------------------------------------------
# Insert data
# --------------------------------------------------

def seed_database(
    clients_count,
    freelancers_count,
    contracts_count,
    audits_count
):

    conn = get_connection()

    try:

        cur = conn.cursor()

        print("Generating clients...")
        clients = generate_clients(clients_count)

        print("Generating freelancers...")
        freelancers = generate_freelancers(freelancers_count)

        print("Generating contracts...")
        contracts = generate_contracts(
            contracts_count,
            clients,
            freelancers
        )

        print("Generating audit logs...")
        audit_logs = generate_audit_logs(
            audits_count,
            clients
        )

        # ------------------------------------------
        # INSERT CLIENTS
        # ------------------------------------------

        print("Inserting clients...")

        cur.executemany(
            """
            INSERT INTO clients
            (id, name, escrow_balance)
            VALUES (%s, %s, %s)
            """,
            clients
        )

        # ------------------------------------------
        # INSERT FREELANCERS
        # ------------------------------------------

        print("Inserting freelancers...")

        cur.executemany(
            """
            INSERT INTO freelancers
            (id, name, latitude, longitude, is_available)
            VALUES (%s, %s, %s, %s, %s)
            """,
            freelancers
        )

        # ------------------------------------------
        # INSERT CONTRACTS
        # ------------------------------------------

        print("Inserting contracts...")

        cur.executemany(
            """
            INSERT INTO contracts
            (id, client_id, freelancer_id,
             budget, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            contracts
        )

        # ------------------------------------------
        # INSERT AUDIT LOGS
        # ------------------------------------------

        print("Inserting audit logs...")

        cur.executemany(
            """
            INSERT INTO wallet_audit_logs
            (id, client_id, amount_changed,
             action_type, balance_after, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            audit_logs
        )

        conn.commit()

        print("\nPostgreSQL seeding completed!")
        print(f"Clients:       {len(clients):,}")
        print(f"Freelancers:   {len(freelancers):,}")
        print(f"Contracts:     {len(contracts):,}")
        print(f"Audit logs:    {len(audit_logs):,}")

    except Exception as e:

        conn.rollback()
        print("ERROR:", e)

    finally:

        cur.close()
        conn.close()


# --------------------------------------------------
# Command-line arguments
# --------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--clients",
        type=int,
        default=DEFAULT_CLIENTS
    )

    parser.add_argument(
        "--freelancers",
        type=int,
        default=DEFAULT_FREELANCERS
    )

    parser.add_argument(
        "--contracts",
        type=int,
        default=DEFAULT_CONTRACTS
    )

    parser.add_argument(
        "--audits",
        type=int,
        default=DEFAULT_AUDITS
    )

    args = parser.parse_args()

    seed_database(
        args.clients,
        args.freelancers,
        args.contracts,
        args.audits
    )