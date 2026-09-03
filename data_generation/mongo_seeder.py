import argparse
import random
import uuid
from datetime import datetime, timedelta, timezone

from faker import Faker
from pymongo import MongoClient

fake = Faker()

# MongoDB connection

def get_database():

    client = MongoClient(
        "mongodb://localhost:27017/"
    )
    return client["gig_task"]

# Geographic regions

CITIES = [
    {
        "name": "Chennai",
        "lat": 13.0827,
        "lon": 80.2707
    },
    {
        "name": "Bengaluru",
        "lat": 12.9716,
        "lon": 77.5946
    },
    {
        "name": "Hyderabad",
        "lat": 17.3850,
        "lon": 78.4867
    },
    {
        "name": "Mumbai",
        "lat": 19.0760,
        "lon": 72.8777
    },
    {
        "name": "Delhi",
        "lat": 28.6139,
        "lon": 77.2090
    }
]


# Portfolio documents

def generate_portfolios(count):

    documents = []

    for _ in range(count):

        certifications = []

        certification_names = [
            "Safety Certified",
            "Licensed Technician",
            "First Aid",
            "Equipment Certified",
            "Professional Training"
        ]

        for certification in random.sample(
            certification_names,
            k=random.randint(0, 3)
        ):
            certifications.append({
                "name": certification,
                "issuer": fake.company(),
                "year": random.randint(2018, 2026)
            })

        documents.append({
            "_id": str(uuid.uuid4()),

            "freelancer_id": str(uuid.uuid4()),

            "bio": fake.paragraph(),

            "skills": random.sample(
                [
                    "Plumbing",
                    "Electrical",
                    "Delivery",
                    "Carpentry",
                    "Cleaning",
                    "Painting",
                    "Repair",
                    "Moving",
                    "Assembly",
                    "Maintenance"
                ],
                k=random.randint(2, 5)
            ),

            "certifications": certifications,

            "projects": [
                {
                    "title": fake.sentence(nb_words=4),
                    "description": fake.paragraph(nb_sentences=2),
                    "completed_at": fake.date_time_between(
                        start_date="-2 years",
                        end_date="now",
                        tzinfo=timezone.utc
                    )
                }
                for _ in range(random.randint(0, 3))
            ],

            "created_at": fake.date_time_between(
                start_date="-2 years",
                end_date="now",
                tzinfo=timezone.utc
            )
        })

    return documents

# Review documents


def generate_reviews(count):

    documents = []

    skill_tags = [
        "Plumbing",
        "Electrical",
        "Cleaning",
        "Carpentry",
        "Delivery",
        "Painting",
        "Repair"
    ]

    for _ in range(count):

        documents.append({

            "_id": str(uuid.uuid4()),

            "freelancer_id": str(uuid.uuid4()),

            "rating": random.randint(1, 5),

            "skill_tags": random.sample(
                skill_tags,
                k=random.randint(1, 3)
            ),

            "review_text": fake.sentence(),

            "created_at": fake.date_time_between(
                start_date="-1 year",
                end_date="now",
                tzinfo=timezone.utc
            )
        })

    return documents

# Worker location pings

def generate_location_pings(count):

    documents = []

    for _ in range(count):

        city = random.choice(CITIES)

        latitude = (
            city["lat"] +
            random.uniform(-0.15, 0.15)
        )

        longitude = (
            city["lon"] +
            random.uniform(-0.15, 0.15)
        )

        documents.append({

            "freelancer_id": str(uuid.uuid4()),

            "location": {
                "type": "Point",

                "coordinates": [
                    longitude,
                    latitude
                ]
            },

            "is_available": random.choice(
                [True, True, True, False]
            ),

            "created_at": (
                datetime.now(timezone.utc)
                -
                timedelta(
                    minutes=random.randint(0, 120)
                )
            )
        })

    return documents


# Main seeding function


def seed_database(
    portfolio_count,
    review_count,
    location_count
):

    db = get_database()

    portfolios = db["Portfolios"]
    reviews = db["GigReviews"]
    locations = db["WorkerLocations"]

    
    # Portfolios

    print("Generating portfolios...")

    portfolio_data = generate_portfolios(
        portfolio_count
    )

    if portfolio_data:
        portfolios.insert_many(
            portfolio_data
        )

    print(
        f"Inserted {len(portfolio_data):,} portfolios."
    )

    # Reviews

    print("Generating reviews...")

    review_data = generate_reviews(
        review_count
    )

    if review_data:
        reviews.insert_many(
            review_data
        )

    print(
        f"Inserted {len(review_data):,} reviews."
    )

  
    # Locations
  

    print("Generating worker locations...")


    batch_size = 5_000

    remaining = location_count

    while remaining > 0:

        current_batch = min(
            batch_size,
            remaining
        )

        batch = generate_location_pings(
            current_batch
        )

        locations.insert_many(batch)

        remaining -= current_batch

        print(
            f"Inserted "
            f"{location_count - remaining:,}/"
            f"{location_count:,}"
        )

    print("\nMongoDB seeding completed!")


# Command-line arguments

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--portfolios",
        type=int,
        default=5000
    )

    parser.add_argument(
        "--reviews",
        type=int,
        default=100000
    )

    parser.add_argument(
        "--locations",
        type=int,
        default=600000
    )

    args = parser.parse_args()

    seed_database(
        args.portfolios,
        args.reviews,
        args.locations
    )
