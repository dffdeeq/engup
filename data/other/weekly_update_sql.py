WEEKLY_UPDATE_SQL = """
WITH ActivityData AS (
    SELECT
        a.user_id,
        MAX(CASE WHEN a.activity_timestamp >= current_date - INTERVAL '14 days' AND a.activity_timestamp < current_date - INTERVAL '7 days' THEN 1 ELSE 0 END) AS active_two_weeks_ago,
        MAX(CASE WHEN a.activity_timestamp >= current_date - INTERVAL '7 days' AND a.activity_timestamp < current_date THEN 1 ELSE 0 END) AS active_last_week,
        BOOL_OR(a.activity_id = 141000 AND a.activity_timestamp >= current_date - INTERVAL '7 days' AND a.activity_timestamp < current_date) AS is_pay_user,
        COUNT(*) FILTER (WHERE a.activity_timestamp >= current_date - INTERVAL '7 days' AND a.activity_timestamp < current_date) > 0 AS is_active_user,
        BOOL_OR(a.activity_timestamp < current_date - INTERVAL '14 days') AS was_active_before_two_weeks
    FROM
        tg_user_activity a
    GROUP BY
        a.user_id
),
UserNewness AS (
    SELECT
        u.id AS user_id,
        (current_date - u.created_at <= INTERVAL '7 days') AS is_new_user,
        u.pts > 0 AS is_premium_user,
        u.created_at < current_date - INTERVAL '7 days' AS is_old_enough_for_return
    FROM
        tg_user u
)
INSERT INTO tg_user_status (user_id, flag_new_user, flag_active_user, flag_pay_user, flag_churn_user, flag_premium_user, flag_return_user, status_date)
SELECT
    ad.user_id,
    un.is_new_user,
    ad.is_active_user,
    ad.is_pay_user,
    (ad.active_two_weeks_ago = 1 AND ad.active_last_week = 0) AS flag_churn_user,
    (ad.is_active_user AND un.is_premium_user) AS flag_premium_user,
    (un.is_old_enough_for_return AND ad.active_two_weeks_ago = 0 AND ad.active_last_week = 1 AND ad.was_active_before_two_weeks) AS flag_return_user,
    current_date
FROM
    ActivityData ad
JOIN
    UserNewness un ON ad.user_id = un.user_id;
"""
