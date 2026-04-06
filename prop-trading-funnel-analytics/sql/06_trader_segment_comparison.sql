WITH payout_by_challenge AS (
    SELECT
        challenge_id,
        SUM(CASE WHEN payout_status IN ('approved', 'under_review') THEN payout_amount_usd ELSE 0 END) AS payout_exposure_usd,
        MAX(CASE WHEN payout_status = 'approved' THEN 1 ELSE 0 END) AS approved_payout_flag
    FROM payouts
    GROUP BY 1
),
segment_challenge_rollup AS (
    SELECT
        u.acquisition_channel,
        u.prior_trading_experience,
        COUNT(DISTINCT u.user_id) AS purchasing_users,
        COUNT(c.challenge_id) AS challenges,
        COUNT(CASE WHEN cp.phase_1_status = 'passed' THEN 1 END) AS phase_1_passed,
        COUNT(CASE WHEN cp.funded_at IS NOT NULL THEN 1 END) AS funded_challenges,
        COUNT(CASE WHEN pb.approved_payout_flag = 1 THEN 1 END) AS approved_payout_challenges,
        SUM(c.price_usd) AS revenue_usd,
        SUM(COALESCE(pb.payout_exposure_usd, 0)) AS payout_exposure_usd
    FROM users AS u
    INNER JOIN challenges AS c
        ON u.user_id = c.user_id
    INNER JOIN challenge_progress AS cp
        ON c.challenge_id = cp.challenge_id
    LEFT JOIN payout_by_challenge AS pb
        ON c.challenge_id = pb.challenge_id
    GROUP BY 1, 2
),
segment_registration_rollup AS (
    SELECT
        acquisition_channel,
        prior_trading_experience,
        COUNT(*) AS registrations
    FROM users
    GROUP BY 1, 2
),
behavior_rollup AS (
    SELECT
        u.acquisition_channel,
        u.prior_trading_experience,
        AVG(tb.avg_daily_sessions) AS avg_daily_sessions,
        AVG(tb.avg_trade_duration_minutes) AS avg_trade_duration_minutes,
        AVG(tb.avg_risk_per_trade_pct) AS avg_risk_per_trade_pct,
        AVG(tb.avg_win_rate) AS avg_win_rate,
        AVG(tb.avg_rr) AS avg_rr,
        AVG(tb.max_drawdown_pct) AS avg_max_drawdown_pct,
        AVG(tb.rule_violations_count) AS avg_rule_violations_count,
        AVG(tb.inactivity_days_after_purchase) AS avg_inactivity_days_after_purchase
    FROM trader_behavior AS tb
    INNER JOIN users AS u
        ON tb.user_id = u.user_id
    GROUP BY 1, 2
),
joined AS (
    SELECT
        sr.acquisition_channel || ' | ' || sr.prior_trading_experience AS segment_name,
        sr.acquisition_channel,
        sr.prior_trading_experience,
        sr.registrations,
        COALESCE(sc.purchasing_users, 0) AS purchasing_users,
        COALESCE(sc.challenges, 0) AS challenges,
        COALESCE(sc.phase_1_passed, 0) AS phase_1_passed,
        COALESCE(sc.funded_challenges, 0) AS funded_challenges,
        COALESCE(sc.approved_payout_challenges, 0) AS approved_payout_challenges,
        COALESCE(sc.revenue_usd, 0) AS revenue_usd,
        COALESCE(sc.payout_exposure_usd, 0) AS payout_exposure_usd,
        br.avg_daily_sessions,
        br.avg_trade_duration_minutes,
        br.avg_risk_per_trade_pct,
        br.avg_win_rate,
        br.avg_rr,
        br.avg_max_drawdown_pct,
        br.avg_rule_violations_count,
        br.avg_inactivity_days_after_purchase
    FROM segment_registration_rollup AS sr
    LEFT JOIN segment_challenge_rollup AS sc
        ON sr.acquisition_channel = sc.acquisition_channel
        AND sr.prior_trading_experience = sc.prior_trading_experience
    LEFT JOIN behavior_rollup AS br
        ON sr.acquisition_channel = br.acquisition_channel
        AND sr.prior_trading_experience = br.prior_trading_experience
),
scored AS (
    SELECT
        *,
        ROUND(100.0 * purchasing_users / NULLIF(registrations, 0), 2) AS registration_to_purchase_pct,
        ROUND(100.0 * funded_challenges / NULLIF(challenges, 0), 2) AS challenge_to_funded_pct,
        ROUND(100.0 * approved_payout_challenges / NULLIF(funded_challenges, 0), 2) AS funded_to_payout_pct,
        ROUND(revenue_usd - payout_exposure_usd, 2) AS gross_profit_proxy_usd,
        CASE
            WHEN purchasing_users / NULLIF(registrations, 0) > AVG(purchasing_users / NULLIF(registrations, 0)) OVER ()
                 AND (revenue_usd - payout_exposure_usd) < AVG(revenue_usd - payout_exposure_usd) OVER ()
                THEN 1
            ELSE 0
        END AS misleading_top_funnel_flag
    FROM joined
)
SELECT
    segment_name,
    acquisition_channel,
    prior_trading_experience,
    registrations,
    purchasing_users,
    challenges,
    phase_1_passed,
    funded_challenges,
    approved_payout_challenges,
    registration_to_purchase_pct,
    challenge_to_funded_pct,
    funded_to_payout_pct,
    ROUND(revenue_usd, 2) AS revenue_usd,
    ROUND(payout_exposure_usd, 2) AS payout_exposure_usd,
    gross_profit_proxy_usd,
    ROUND(avg_daily_sessions, 2) AS avg_daily_sessions,
    ROUND(avg_trade_duration_minutes, 2) AS avg_trade_duration_minutes,
    ROUND(avg_risk_per_trade_pct, 2) AS avg_risk_per_trade_pct,
    ROUND(avg_win_rate, 3) AS avg_win_rate,
    ROUND(avg_rr, 2) AS avg_rr,
    ROUND(avg_max_drawdown_pct, 2) AS avg_max_drawdown_pct,
    ROUND(avg_rule_violations_count, 2) AS avg_rule_violations_count,
    ROUND(avg_inactivity_days_after_purchase, 2) AS avg_inactivity_days_after_purchase,
    misleading_top_funnel_flag,
    DENSE_RANK() OVER (ORDER BY gross_profit_proxy_usd DESC) AS value_rank
FROM scored
WHERE registrations >= 180
ORDER BY value_rank, registrations DESC;
