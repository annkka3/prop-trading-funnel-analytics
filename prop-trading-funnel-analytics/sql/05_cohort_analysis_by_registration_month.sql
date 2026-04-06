WITH phase_user_flags AS (
    SELECT
        c.user_id,
        MAX(CASE WHEN cp.phase_1_status = 'passed' THEN 1 ELSE 0 END) AS phase_1_pass_user_flag,
        MAX(CASE WHEN cp.phase_2_status = 'passed' THEN 1 ELSE 0 END) AS phase_2_pass_user_flag,
        MAX(CASE WHEN cp.funded_at IS NOT NULL THEN 1 ELSE 0 END) AS funded_user_flag
    FROM challenges AS c
    INNER JOIN challenge_progress AS cp
        ON c.challenge_id = cp.challenge_id
    GROUP BY 1
),
payout_user_flags AS (
    SELECT
        user_id,
        MAX(CASE WHEN payout_status = 'approved' THEN 1 ELSE 0 END) AS payout_user_flag
    FROM payouts
    GROUP BY 1
),
cohort_rollup AS (
    SELECT
        DATE_TRUNC('month', u.registration_date) AS registration_month,
        COUNT(*) AS registrations,
        COUNT(CASE WHEN k.kyc_status = 'verified' THEN 1 END) AS kyc_verified_users,
        COUNT(CASE WHEN c.user_id IS NOT NULL THEN 1 END) AS purchasing_users,
        COUNT(CASE WHEN p.phase_1_pass_user_flag = 1 THEN 1 END) AS phase_1_pass_users,
        COUNT(CASE WHEN p.phase_2_pass_user_flag = 1 THEN 1 END) AS phase_2_pass_users,
        COUNT(CASE WHEN p.funded_user_flag = 1 THEN 1 END) AS funded_users,
        COUNT(CASE WHEN pu.payout_user_flag = 1 THEN 1 END) AS payout_users
    FROM users AS u
    LEFT JOIN kyc_events AS k
        ON u.user_id = k.user_id
    LEFT JOIN (
        SELECT DISTINCT user_id
        FROM challenges
    ) AS c
        ON u.user_id = c.user_id
    LEFT JOIN phase_user_flags AS p
        ON u.user_id = p.user_id
    LEFT JOIN payout_user_flags AS pu
        ON u.user_id = pu.user_id
    GROUP BY 1
)
SELECT
    registration_month,
    registrations,
    ROUND(100.0 * kyc_verified_users / NULLIF(registrations, 0), 2) AS kyc_verified_rate_pct,
    ROUND(100.0 * purchasing_users / NULLIF(registrations, 0), 2) AS purchase_rate_pct,
    ROUND(100.0 * phase_1_pass_users / NULLIF(registrations, 0), 2) AS phase_1_pass_rate_pct,
    ROUND(100.0 * phase_2_pass_users / NULLIF(registrations, 0), 2) AS phase_2_pass_rate_pct,
    ROUND(100.0 * funded_users / NULLIF(registrations, 0), 2) AS funded_rate_pct,
    ROUND(100.0 * payout_users / NULLIF(registrations, 0), 2) AS payout_rate_pct
FROM cohort_rollup
ORDER BY registration_month;

