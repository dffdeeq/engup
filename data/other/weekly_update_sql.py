WEEKLY_UPDATE_SQL = """
WITH WeekCalculation AS (
    SELECT 
        EXTRACT(WEEK FROM CURRENT_DATE) AS current_week,
        EXTRACT(WEEK FROM CURRENT_DATE) - 1 AS week_minus_1,
        EXTRACT(WEEK FROM CURRENT_DATE) - 2 AS week_minus_2
),
ActivityData AS (
  SELECT
        a.user_id,
        BOOL_OR(a.activity_name = 'buy points' AND EXTRACT(WEEK FROM a.activity_timestamp) = wc.week_minus_1) AS is_pay_user,
        COUNT(*) FILTER (WHERE EXTRACT(WEEK FROM a.activity_timestamp) = wc.week_minus_1) > 0 AS is_active_user,
        BOOL_OR(EXTRACT(WEEK FROM a.activity_timestamp) = wc.week_minus_2) AS is_active_two_weeks_ago
    FROM
        tg_user_activity a,
        WeekCalculation wc
    WHERE 
        EXTRACT(WEEK FROM a.activity_timestamp) IN (wc.week_minus_1, wc.week_minus_2)
    GROUP BY
        a.user_id
),
UserNewness AS (
 SELECT
    u.id AS user_id,
    (EXTRACT(WEEK FROM u.created_at) = wc.week_minus_1) AS is_new_user, 
    u.pts > 0 AS is_premium_user, 
    (EXTRACT(WEEK FROM u.created_at) <> wc.week_minus_1) AS is_old_enough_for_return 
FROM
    tg_user u   
JOIN
    ActivityData a
    ON u.id = a.user_id
CROSS JOIN
    WeekCalculation wc
)
INSERT INTO tg_user_status (
    user_id, 
    flag_new_user, 
    flag_active_user, 
    flag_pay_user, 
    flag_churn_user, 
    flag_premium_user, 
    flag_return_user, 
    status_date)
SELECT
    ad.user_id,
    un.is_new_user,
    ad.is_active_user,
    ad.is_pay_user,
    (ad.is_active_two_weeks_ago = true AND ad.is_active_user = false) AS flag_churn_user,
     un.is_premium_user AS flag_premium_user,
    (un.is_old_enough_for_return AND NOT ad.is_active_two_weeks_ago AND ad.is_active_user) AS flag_return_user,
   (TO_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::text || ' ' || wc.week_minus_1::text, 'IYYY IW') + INTERVAL '6 days')::date AS status_date
FROM
    ActivityData ad
JOIN
    UserNewness un ON ad.user_id = un.user_id
CROSS JOIN
    WeekCalculation wc;
"""
