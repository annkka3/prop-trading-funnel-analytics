WITH approved_payout_challenges AS (
    SELECT DISTINCT challenge_id
    FROM payouts
    WHERE payout_status = 'approved'
),
funnel_counts AS (
    SELECT 1 AS stage_order, 'Registered' AS stage_name, 'user' AS stage_grain, COUNT(*) AS entity_count
    FROM users

    UNION ALL

    SELECT 2, 'KYC Started', 'user', COUNT(*)
    FROM kyc_events
    WHERE kyc_status <> 'not_started'

    UNION ALL

    SELECT 3, 'KYC Verified', 'user', COUNT(*)
    FROM kyc_events
    WHERE kyc_status = 'verified'

    UNION ALL

    SELECT 4, 'Purchased Challenge', 'user', COUNT(DISTINCT user_id)
    FROM challenges

    UNION ALL

    SELECT 5, 'Passed Phase 1', 'challenge', COUNT(*)
    FROM challenge_progress
    WHERE phase_1_status = 'passed'

    UNION ALL

    SELECT 6, 'Passed Phase 2', 'challenge', COUNT(*)
    FROM challenge_progress
    WHERE phase_2_status = 'passed'

    UNION ALL

    SELECT 7, 'Funded', 'challenge', COUNT(*)
    FROM challenge_progress
    WHERE funded_at IS NOT NULL

    UNION ALL

    SELECT 8, 'Approved Payout', 'challenge', COUNT(*)
    FROM approved_payout_challenges
),
annotated AS (
    SELECT
        stage_order,
        stage_name,
        stage_grain,
        entity_count,
        LAG(entity_count) OVER (ORDER BY stage_order) AS previous_stage_count,
        FIRST_VALUE(entity_count) OVER (ORDER BY stage_order) AS first_stage_count
    FROM funnel_counts
)
SELECT
    stage_order,
    stage_name,
    stage_grain,
    entity_count,
    ROUND(100.0 * entity_count / NULLIF(previous_stage_count, 0), 2) AS conversion_from_previous_pct,
    ROUND(100.0 * entity_count / NULLIF(first_stage_count, 0), 2) AS conversion_from_registered_pct
FROM annotated
ORDER BY stage_order;

