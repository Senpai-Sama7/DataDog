-- 7-day activation and retention example
WITH signups AS (
  SELECT user_id, DATE(event_date) AS signup_date, channel, region
  FROM events
  WHERE event_type='signup'
),
activations AS (
  SELECT e.user_id, MIN(DATE(e.event_date)) AS activation_date
  FROM events e JOIN signups s USING(user_id)
  WHERE e.event_type='activate' AND DATE(e.event_date) BETWEEN s.signup_date AND DATE(s.signup_date, '+7 day')
  GROUP BY e.user_id
),
d7_sessions AS (
  SELECT e.user_id
  FROM events e JOIN signups s USING(user_id)
  WHERE e.event_type='session' AND DATE(e.event_date) BETWEEN s.signup_date AND DATE(s.signup_date, '+7 day')
  GROUP BY e.user_id
)
SELECT
  strftime('%Y-%m', signup_date) AS signup_month,
  channel,
  COUNT(*) AS signups,
  COUNT(a.user_id) AS d7_activated,
  ROUND(100.0 * COUNT(a.user_id)/COUNT(*), 1) AS d7_activation_rate_pct,
  COUNT(d.user_id) AS d7_retained,
  ROUND(100.0 * COUNT(d.user_id)/COUNT(*), 1) AS d7_retention_rate_pct
FROM signups s
LEFT JOIN activations a ON a.user_id = s.user_id
LEFT JOIN d7_sessions d ON d.user_id = s.user_id
GROUP BY 1,2
ORDER BY 1,2;
