// GigTask - Workflow 3: Nearest Available Worker
//
// Requirement:
// Write a $geoNear pipeline to find the closest available freelancer
// to a physical job site.
//
// IMPORTANT:
// $geoNear must be the first stage in the aggregation pipeline.
// Coordinates use GeoJSON order: [longitude, latitude].
//
// Run with mongosh after loading WorkerLocations.

//use gigtask_db;

// -----------------------------------------------------------------------------
// Job-site coordinates.
// Replace these with the actual physical job site's coordinates.
// Example below is Hyderabad, India.
// -----------------------------------------------------------------------------
const jobLongitude = 78.4867;
const jobLatitude  = 17.3850;

// 5 km = 5000 metres.
const maxDistanceMeters = 5000;

// -----------------------------------------------------------------------------
// $geoNear finds documents from nearest to farthest and calculates distance.
// The query filters for currently available workers.
// -----------------------------------------------------------------------------
const nearestAvailableWorkers = db.WorkerLocations.aggregate([
  {
    $geoNear: {
      near: {
        type: "Point",
        coordinates: [jobLongitude, jobLatitude]
      },
      key: "location",
      distanceField: "distance_meters",
      maxDistance: maxDistanceMeters,
      spherical: true,
      query: {
        is_available: true
      }
    }
  },
  {
    $project: {
      _id: 1,
      freelancer_id: 1,
      is_available: 1,
      location: 1,
      created_at: 1,
      distance_meters: 1,
      distance_km: {
        $round: [
          { $divide: ["$distance_meters", 1000] },
          3
        ]
      }
    }
  },
  {
    $limit: 20
  }
]);

print("Nearest available workers within 5 km:");
nearestAvailableWorkers.forEach(doc => printjson(doc));

// -----------------------------------------------------------------------------
// Performance proof.
//
// Execute this separately after confirming the normal pipeline works:
//
// db.WorkerLocations.explain("executionStats").aggregate([...same pipeline...])
//
// The explain output should demonstrate use of the 2dsphere index rather than
// a collection scan. Save the raw output in:
// performance/mongo_execution_stats.json
// -----------------------------------------------------------------------------
