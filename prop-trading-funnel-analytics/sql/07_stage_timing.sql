-- Median time between funnel transitions.
-- Each CTE returns one row; CROSS JOIN at the end is safe and intentional.
-- Median is used throughout because stage durations are right-skewed —
-- a handful of slow KYC completions or delayed payout requests would pull
-- the mean far from the typical experience.

WITH reg_to_kyc AS (
    SELECT
        COUNT(*)                                                                           AS n,
        ROUND(MEDIAN(DATE_DIFF('day', u.registration_date, k.kyc_completed_at)), 1)       AS median_days,
        ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (
            ORDER BY DATE_DIFF('day', u.registration_date, k.kyc_completed_at)), 1)       AS p25_days,
        ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (
            ORDER BY DATE_DIFF('day', u.registration_date, k.kyc_completed_at)), 1)       AS p75_days
    FROM users AS u
    INNER JOIN kyc_events AS k
        ON u.user_id = k.user_id
    WHERE k.kyc_status = 'verified'
),
kyc_to_purchase AS (
    SELECT
        COUNT(*)                                                                           AS n,
        ROUND(MEDIAN(DATE_DIFF('day', k.kyc_completed_at, fp.first_purchase_date)), 1)    AS median_days,
        ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (
            ORDER BY DATE_DIFF('day', k.kyc_completed_at, fp.first_purchase_date)), 1)    AS p75_days
    FROM kyc_events AS k
    INNER JOIN (
        SELECT user_id, MIN(purchase_date) AS first_purchase_date
        FROM challenges
        GROUP BY 1
    ) AS fp ON k.user_id = fp.user_id
    WHERE k.kyc_status = 'verified'
),
phase1 AS (
    SELECT
        COUNT(*)                                                                           AS n,
        ROUND(MEDIAN(CASE WHEN cp.phase_1_status = 'passed'
            THEN DATE_DIFF('day', c.purchase_date, cp.phase_1_completed_at) END), 1)      AS median_days_pass,
        ROUND(MEDIAN(CASE WHEN cp.phase_1_status = 'failed'
            THEN DATE_DIFF('day', c.purchase_date, cp.phase_1_completed_at) END), 1)      AS median_days_fail
    FROM challenge_progress AS cp
    INNER JOIN challenges AS c
        ON cp.challenge_id = c.challenge_id
    WHERE cp.phase_1_completed_at IS NOT NULL
),
phase2 AS (
    SELECT
        COUNT(*)                                                                           AS n,
        ROUND(MEDIAN(CASE WHEN cp.phase_2_status = 'passed'
            THEN DATE_DIFF('day', cp.phase_1_completed_at, cp.phase_2_completed_at) END), 1) AS median_days_pass,
        ROUND(MEDIAN(CASE WHEN cp.phase_2_status = 'failed'
            THEN DATE_DIFF('day', cp.phase_1_completed_at, cp.phase_2_completed_at) END), 1) AS median_days_fail
    FROM challenge_progress AS cp
    WHERE cp.phase_2_status IS NOT NULL
      AND cp.phase_2_status <> 'not_reached'
      AND cp.phase_1_completed_at IS NOT NULL
      AND cp.phase_2_completed_at IS NOT NULL
),
funded_to_payout AS (
    SELECT
        COUNT(*)                                                                           AS n,
        ROUND(MEDIAN(DATE_DIFF('day', cp.funded_at, fp.first_payout_at)), 1)              AS median_days,
        ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (
            ORDER BY DATE_DIFF('day', cp.funded_at, fp.first_payout_at)), 1)              AS p25_days,
        ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (
            ORDER BY DATE_DIFF('day', cp.funded_at, fp.first_payout_at)), 1)              AS p75_days
    FROM challenge_progress AS cp
    INNER JOIN (
        SELECT challenge_id, MIN(payout_requested_at) AS first_payout_at
        FROM payouts
        WHERE payout_status IN ('approved', 'under_review')
        GROUP BY 1
    ) AS fp ON cp.challenge_id = fp.challenge_id
    WHERE cp.funded_at IS NOT NULL
)
SELECT
    r.n                    AS reg_to_kyc_verified_n,
    r.median_days          AS reg_to_kyc_median_days,
    r.p25_days             AS reg_to_kyc_p25_days,
    r.p75_days             AS reg_to_kyc_p75_days,

    kp.n                   AS kyc_to_purchase_n,
    kp.median_days         AS kyc_to_purchase_median_days,
    kp.p75_days            AS kyc_to_purchase_p75_days,

    p1.n                   AS phase1_n,
    p1.median_days_pass    AS phase1_pass_median_days,
    p1.median_days_fail    AS phase1_fail_median_days,

    p2.n                   AS phase2_n,
    p2.median_days_pass    AS phase2_pass_median_days,
    p2.median_days_fail    AS phase2_fail_median_days,

    fp.n                   AS funded_to_payout_n,
    fp.median_days         AS funded_to_payout_median_days,
    fp.p25_days            AS funded_to_payout_p25_days,
    fp.p75_days            AS funded_to_payout_p75_days

FROM reg_to_kyc AS r
CROSS JOIN kyc_to_purchase AS kp
CROSS JOIN phase1 AS p1
CROSS JOIN phase2 AS p2
CROSS JOIN funded_to_payout AS fp;
