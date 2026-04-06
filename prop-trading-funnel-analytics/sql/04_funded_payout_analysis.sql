WITH payout_by_challenge AS (
    SELECT
        challenge_id,
        COUNT(*) AS payout_requests,
        SUM(CASE WHEN payout_status = 'approved' THEN payout_amount_usd ELSE 0 END) AS approved_payout_usd,
        SUM(CASE WHEN payout_status IN ('approved', 'under_review') THEN payout_amount_usd ELSE 0 END) AS payout_exposure_usd,
        MAX(CASE WHEN payout_status = 'approved' THEN 1 ELSE 0 END) AS approved_payout_flag,
        MAX(CASE WHEN payout_status = 'under_review' THEN 1 ELSE 0 END) AS under_review_flag
    FROM payouts
    GROUP BY 1
),
funded_base AS (
    SELECT
        u.acquisition_channel,
        u.prior_trading_experience,
        c.challenge_id,
        c.challenge_type,
        c.price_usd,
        c.account_size,
        COALESCE(pb.payout_requests, 0) AS payout_requests,
        COALESCE(pb.approved_payout_usd, 0) AS approved_payout_usd,
        COALESCE(pb.payout_exposure_usd, 0) AS payout_exposure_usd,
        COALESCE(pb.approved_payout_flag, 0) AS approved_payout_flag,
        COALESCE(pb.under_review_flag, 0) AS under_review_flag
    FROM challenge_progress AS cp
    INNER JOIN challenges AS c
        ON cp.challenge_id = c.challenge_id
    INNER JOIN users AS u
        ON c.user_id = u.user_id
    LEFT JOIN payout_by_challenge AS pb
        ON cp.challenge_id = pb.challenge_id
    WHERE cp.funded_at IS NOT NULL
),
segment_rollup AS (
    SELECT
        acquisition_channel || ' | ' || prior_trading_experience AS segment_name,
        acquisition_channel,
        prior_trading_experience,
        COUNT(*) AS funded_challenges,
        COUNT(CASE WHEN approved_payout_flag = 1 THEN 1 END) AS approved_payout_challenges,
        COUNT(CASE WHEN payout_requests > 0 THEN 1 END) AS payout_request_challenges,
        AVG(price_usd) AS avg_fee_usd,
        AVG(account_size) AS avg_account_size,
        AVG(payout_requests) AS avg_payout_requests,
        SUM(approved_payout_usd) AS approved_payout_usd,
        SUM(payout_exposure_usd) AS payout_exposure_usd,
        AVG(CASE WHEN under_review_flag = 1 THEN 1.0 ELSE 0.0 END) AS under_review_share
    FROM funded_base
    GROUP BY 1, 2, 3
)
SELECT
    segment_name,
    acquisition_channel,
    prior_trading_experience,
    funded_challenges,
    approved_payout_challenges,
    payout_request_challenges,
    ROUND(100.0 * approved_payout_challenges / NULLIF(funded_challenges, 0), 2) AS payout_rate_pct,
    ROUND(avg_fee_usd, 2) AS avg_fee_usd,
    ROUND(avg_account_size, 0) AS avg_account_size,
    ROUND(avg_payout_requests, 2) AS avg_payout_requests,
    ROUND(approved_payout_usd, 2) AS approved_payout_usd,
    ROUND(payout_exposure_usd, 2) AS payout_exposure_usd,
    ROUND(payout_exposure_usd / NULLIF(funded_challenges, 0), 2) AS exposure_per_funded_challenge_usd,
    ROUND(100.0 * under_review_share, 2) AS under_review_share_pct,
    DENSE_RANK() OVER (ORDER BY payout_exposure_usd DESC) AS exposure_rank,
    DENSE_RANK() OVER (ORDER BY payout_rate_pct DESC) AS payout_rate_rank
FROM segment_rollup
WHERE funded_challenges >= 12
ORDER BY payout_exposure_usd DESC, payout_rate_pct DESC;

