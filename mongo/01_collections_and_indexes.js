// GigTask - Member 3
// MongoDB collection creation, validation, 2dsphere index, and TTL index.
//
// Project 5 requirements:
//   - Portfolios: flexible freelancer skills/certifications
//   - GigReviews: ratings, skill-tags, timestamps
//   - WorkerLocations: real-time worker locations in GeoJSON format
//   - 2dsphere index on WorkerLocations.location
//   - TTL index on WorkerLocations.created_at for 2 hours (7200 seconds)
//
// Run with mongosh.
use gigtask_db;

// -----------------------------------------------------------------------------
// 1. Portfolios
// -----------------------------------------------------------------------------
db.createCollection("Portfolios", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["freelancer_id", "skills", "certifications"],
      properties: {
        freelancer_id: {
          bsonType: ["int", "long", "string"],
          description: "ID of the freelancer in PostgreSQL"
        },
        name: {
          bsonType: "string"
        },
        skills: {
          bsonType: "array",
          items: { bsonType: "string" }
        },
        certifications: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["name"],
            properties: {
              name: { bsonType: "string" },
              issuer: { bsonType: "string" },
              year: { bsonType: ["int", "long"] }
            }
          }
        },
        projects: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              title: { bsonType: "string" },
              description: { bsonType: "string" },
              completed_at: { bsonType: "date" }
            }
          }
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});

// One portfolio document per freelancer.
db.Portfolios.createIndex(
  { freelancer_id: 1 },
  { unique: true, name: "uq_portfolios_freelancer_id" }
);

// Useful for searching freelancers by a skill.
db.Portfolios.createIndex(
  { skills: 1 },
  { name: "idx_portfolios_skills" }
);

// -----------------------------------------------------------------------------
// 2. GigReviews
// -----------------------------------------------------------------------------
db.createCollection("GigReviews", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["freelancer_id", "rating", "skill_tags", "created_at"],
      properties: {
        freelancer_id: {
          bsonType: ["int", "long", "string"]
        },
        contract_id: {
          bsonType: ["int", "long", "string"]
        },
        rating: {
          bsonType: ["int", "long", "double"],
          minimum: 1,
          maximum: 5
        },
        review_text: {
          bsonType: "string"
        },
        skill_tags: {
          bsonType: "array",
          items: { bsonType: "string" }
        },
        created_at: {
          bsonType: "date"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});

db.GigReviews.createIndex(
  { freelancer_id: 1, created_at: -1 },
  { name: "idx_gigrevs_freelancer_created" }
);

db.GigReviews.createIndex(
  { rating: 1 },
  { name: "idx_gigrevs_rating" }
);

// -----------------------------------------------------------------------------
// 3. WorkerLocations
// -----------------------------------------------------------------------------
db.createCollection("WorkerLocations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["freelancer_id", "is_available", "location", "created_at"],
      properties: {
        freelancer_id: {
          bsonType: ["int", "long", "string"]
        },
        is_available: {
          bsonType: "bool"
        },
        location: {
          bsonType: "object",
          required: ["type", "coordinates"],
          properties: {
            type: {
              enum: ["Point"]
            },
            coordinates: {
              bsonType: "array",
              minItems: 2,
              maxItems: 2,
              items: { bsonType: ["double", "int", "long"] }
            }
          }
        },
        created_at: {
          bsonType: "date"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});

// Required geospatial index.
db.WorkerLocations.createIndex(
  { location: "2dsphere" },
  { name: "idx_workerlocations_2dsphere" }
);

// Required 2-hour TTL index.
// MongoDB removes documents after created_at + 7200 seconds.
db.WorkerLocations.createIndex(
  { created_at: 1 },
  { expireAfterSeconds: 7200, name: "idx_workerlocations_ttl_2h" }
);

// Helpful supporting index for filtering available workers.
db.WorkerLocations.createIndex(
  { is_available: 1, freelancer_id: 1 },
  { name: "idx_workerlocations_available_freelancer" }
);

print("GigTask MongoDB collections and indexes created successfully.");
printjson({
  collections: db.getCollectionNames(),
  workerLocationIndexes: db.WorkerLocations.getIndexes()
});
