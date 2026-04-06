WITH kyc_verified_users AS (
    SELECT DISTINCT user_id
    FROM kyc_events
    WHERE kyc_status = 'verified'
),
user_purchase_flags AS (
    SELECT DISTINCT user_id
    FROM challenges
),
payout_by_challenge AS (
    SELECT
        challenge_id,
        SUM(CASE WHEN payout_status IN ('approved', 'under_review') THEN payout_amount_usd ELSE 0 END) AS payout_exposure_usd,
        MAX(CASE WHEN payout_status = 'approved' THEN 1 ELSE 0 END) AS approved_payout_flag
    FROM payouts
    GROUP BY 1
),
challenge_stage AS (
    SELECT
        u.acquisition_channel,
        c.challenge_id,
        c.price_usd,
        cp.phase_1_status,
        cp.phase_2_status,
        CASE WHEN cp.funded_at IS NOT NULL THEN 1 ELSE 0 END AS funded_flag,
        COALESCE(pb.approved_payout_flag, 0) AS approved_payout_flag,
        COALESCE(pb.payout_exposure_usd, 0) AS payout_exposure_usd
    FROM challenges AS c
    INNER JOIN users AS u
        ON c.user_id = u.user_id
    INNER JOIN challenge_progress AS cp
        ON c.challenge_id = cp.challenge_id
    LEFT JOIN payout_by_challenge AS pb
        ON c.challenge_id = pb.challenge_id
),
user_rollup AS (
    SELECT
        u.acquisition_channel,
        COUNT(*) AS registrations,
        COUNT(CASE WHEN kv.user_id IS NOT NULL THEN 1 END) AS kyc_verified_users,
        COUNT(CASE WHEN up.user_id IS NOT NULL THEN 1 END) AS purchasing_users
    FROM users AS u
    LEFT JOIN kyc_verified_users AS kv
        ON u.user_id = kv.user_id
    LEFT JOIN user_purchase_flags AS up
        ON u.user_id = up.user_id
    GROUP BY 1
),
challenge_rollup AS (
    SELECT
        acquisition_channel,
        COUNT(*) AS challenges,
        COUNT(CASE WHEN phase_1_status = 'passed' THEN 1 END) AS phase_1_passed,
        COUNT(CASE WHEN phase_2_status = 'passed' THEN 1 END) AS phase_2_passed,
        SUM(funded_flag) AS funded_challenges,
        SUM(approved_payout_flag) AS approved_payout_challenges,
        SUM(price_usd) AS revenue_usd,
        SUM(payout_exposure_usd) AS payout_exposure_usd
    FROM challenge_stage
    GROUP BY 1
)
SELECT
    ur.acquisition_channel,
    ur.registrations,
    ur.kyc_verified_users,
    ur.purchasing_users,
    cr.challenges,
    cr.phase_1_passed,
    cr.phase_2_passed,
    cr.funded_challenges,
    cr.approved_payout_challenges,
    ROUND(100.0 * ur.kyc_verified_users / NULLIF(ur.registrations, 0), 2) AS registration_to_kyc_verified_pct,
    ROUND(100.0 * ur.purchasing_users / NULLIF(ur.registrations, 0), 2) AS registration_to_purchase_pct,
    ROUND(100.0 * cr.funded_challenges / NULLIF(cr.challenges, 0), 2) AS purchase_to_funded_pct,
    ROUND(100.0 * cr.approved_payout_challenges / NULLIF(cr.funded_challenges, 0), 2) AS funded_to_payout_pct,
    ROUND(100.0 * cr.approved_payout_challenges / NULLIF(cr.challenges, 0), 2) AS challenge_to_payout_pct,
    ROUND(cr.revenue_usd, 2) AS revenue_usd,
    ROUND(cr.payout_exposure_usd, 2) AS payout_exposure_usd,
    ROUND(cr.revenue_usd - cr.payout_exposure_usd, 2) AS gross_profit_proxy_usd,
    ROUND(cr.payout_exposure_usd / NULLIF(cr.revenue_usd, 0), 3) AS payout_exposure_to_fee_ratio
FROM user_rollup AS ur
LEFT JOIN challenge_rollup AS cr
    ON ur.acquisition_channel = cr.acquisition_channel
ORDER BY registrations DESC;

