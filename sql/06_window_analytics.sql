-- cte to aggregate frelancers total revenue per day.
-- budget seems to be only thing that may represent revenue 
WITH freelancer_daily_revenue AS (
    SELECT
        freelancer_id,
        DATE_TRUNC('day', created_at) AS earning_day,
        SUM(budget) AS total_amount
    FROM contracts
    WHERE status = 'COMPLETED'
    GROUP BY freelancer_id, DATE_TRUNC('day', created_at)
), 
--cte to get the 7 day average
seven_day_freelancer_avg AS (
    SELECT
        freelancer_id,
        earning_day,
        total_amount,
        AVG(total_amount) OVER (
            PARTITION BY freelancer_id
            ORDER BY earning_day
            RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW
        ) AS moving_avg_revenue
    FROM freelancer_daily_revenue
),
-- cte for latest 7-day average for a day
latest_freelancer_avg AS (
   SELECT DISTINCT ON (freelancer_id)
    freelancer_id,
    earning_day,
    moving_avg_revenue
FROM seven_day_freelancer_avg
ORDER BY freelancer_id, earning_day DESC
)
SELECT
    freelancer_id,
    earning_day,
    moving_avg_revenue,
    DENSE_RANK() OVER (ORDER BY moving_avg_revenue DESC) AS revenue_rank
FROM latest_freelancer_avg;


