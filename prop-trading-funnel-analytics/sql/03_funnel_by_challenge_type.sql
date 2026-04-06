WITH payout_by_challenge AS (
    SELECT
        challenge_id,
        SUM(CASE WHEN payout_status IN ('approved', 'under_review') THEN payout_amount_usd ELSE 0 END) AS payout_exposure_usd,
        MAX(CASE WHEN payout_status = 'approved' THEN 1 ELSE 0 END) AS approved_payout_flag
    FROM payouts
    GROUP BY 1
),
challenge_base AS (
    SELECT
        c.challenge_type,
        c.challenge_id,
        c.price_usd,
        c.account_size,
        cp.phase_1_status,
        cp.phase_2_status,
        CASE WHEN cp.funded_at IS NOT NULL THEN 1 ELSE 0 END AS funded_flag,
        COALESCE(pb.approved_payout_flag, 0) AS approved_payout_flag,
        COALESCE(pb.payout_exposure_usd, 0) AS payout_exposure_usd
    FROM challenges AS c
    INNER JOIN challenge_progress AS cp
        ON c.challenge_id = cp.challenge_id
    LEFT JOIN payout_by_challenge AS pb
        ON c.challenge_id = pb.challenge_id
),
rollup AS (
    SELECT
        challenge_type,
        COUNT(*) AS challenges,
        AVG(price_usd) AS avg_price_usd,
        AVG(account_size) AS avg_account_size,
        COUNT(CASE WHEN phase_1_status = 'passed' THEN 1 END) AS phase_1_passed,
        COUNT(CASE WHEN phase_2_status = 'passed' THEN 1 END) AS phase_2_passed,
        SUM(funded_flag) AS funded_challenges,
        SUM(approved_payout_flag) AS approved_payout_challenges,
        SUM(price_usd) AS revenue_usd,
        SUM(payout_exposure_usd) AS payout_exposure_usd
    FROM challenge_base
    GROUP BY 1
)
SELECT
    challenge_type,
    challenges,
    ROUND(avg_price_usd, 2) AS avg_price_usd,
    ROUND(avg_account_size, 0) AS avg_account_size,
    ROUND(100.0 * phase_1_passed / NULLIF(challenges, 0), 2) AS phase_1_pass_rate_pct,
    ROUND(100.0 * phase_2_passed / NULLIF(phase_1_passed, 0), 2) AS phase_2_pass_rate_pct,
    ROUND(100.0 * funded_challenges / NULLIF(challenges, 0), 2) AS funded_rate_pct,
    ROUND(100.0 * approved_payout_challenges / NULLIF(funded_challenges, 0), 2) AS payout_rate_pct,
    ROUND(revenue_usd, 2) AS revenue_usd,
    ROUND(payout_exposure_usd, 2) AS payout_exposure_usd,
    ROUND(revenue_usd - payout_exposure_usd, 2) AS gross_profit_proxy_usd,
    ROUND(payout_exposure_usd / NULLIF(revenue_usd, 0), 3) AS payout_exposure_to_fee_ratio,
    DENSE_RANK() OVER (ORDER BY gross_profit_proxy_usd DESC) AS value_rank,
    DENSE_RANK() OVER (ORDER BY payout_exposure_usd DESC) AS exposure_rank
FROM rollup
ORDER BY challenges DESC;

