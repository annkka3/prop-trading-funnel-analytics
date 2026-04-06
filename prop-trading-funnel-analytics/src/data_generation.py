from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.config import (
    ACQUISITION_WEIGHTS,
    AGE_WEIGHTS_BY_CHANNEL,
    CHALLENGE_PRODUCTS,
    CHALLENGE_TYPE_WEIGHTS,
    COUNTRY_LANGUAGE_OPTIONS,
    COUNTRY_QUALITY_ADJUSTMENT,
    COUNTRY_WEIGHTS,
    DATA_DIR,
    DEVICE_WEIGHTS_BY_CHANNEL,
    EXPERIENCE_LEVELS,
    EXPERIENCE_SCORE,
    EXPERIENCE_WEIGHTS_BY_CHANNEL,
    PROMO_CODES,
    RANDOM_SEED,
    REGISTRATION_END,
    REGISTRATION_START,
    USER_COUNT,
)


CHANNEL_DISCIPLINE = {
    "organic": 0.05,
    "paid_social": -0.12,
    "affiliates": -0.05,
    "influencers": -0.16,
    "direct": 0.17,
    "community": 0.14,
}

CHANNEL_ENGAGEMENT = {
    "organic": 0.02,
    "paid_social": -0.08,
    "affiliates": 0.01,
    "influencers": -0.10,
    "direct": 0.18,
    "community": 0.16,
}

CHANNEL_RISK = {
    "organic": -0.02,
    "paid_social": 0.14,
    "affiliates": 0.11,
    "influencers": 0.17,
    "direct": -0.03,
    "community": -0.04,
}

AGE_QUALITY = {
    "18-24": -0.08,
    "25-34": 0.04,
    "35-44": 0.07,
    "45-54": 0.05,
    "55+": 0.01,
}

AGE_RISK = {
    "18-24": 0.12,
    "25-34": 0.03,
    "35-44": -0.02,
    "45-54": -0.05,
    "55+": -0.08,
}

CHALLENGE_DIFFICULTY = {
    "standard": 0.10,
    "aggressive": -0.28,
    "swing": 0.18,
    "low_cost_trial": -0.42,
}

CHALLENGE_PAYOUT_BOOST = {
    "standard": 0.05,
    "aggressive": 0.12,
    "swing": 0.18,
    "low_cost_trial": -0.22,
}

PROMO_WEIGHTS = {
    "organic": 0.20,
    "paid_social": 0.58,
    "affiliates": 0.51,
    "influencers": 0.48,
    "direct": 0.15,
    "community": 0.29,
}


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + np.exp(-value))


def normalize_weights(weights: dict[Any, float]) -> dict[Any, float]:
    cleaned = {key: max(float(value), 0.001) for key, value in weights.items()}
    total = sum(cleaned.values())
    return {key: value / total for key, value in cleaned.items()}


def choose_weighted(rng: np.random.Generator, weights: dict[Any, float]) -> Any:
    normalized = normalize_weights(weights)
    keys = list(normalized.keys())
    index = int(rng.choice(len(keys), p=list(normalized.values())))
    return keys[index]


def sample_registration_dates(rng: np.random.Generator, n_users: int) -> pd.Series:
    calendar = pd.date_range(REGISTRATION_START, REGISTRATION_END, freq="D")
    month_weights = {
        1: 1.18,
        2: 0.94,
        3: 1.00,
        4: 1.02,
        5: 1.04,
        6: 0.95,
        7: 0.88,
        8: 0.87,
        9: 1.10,
        10: 1.08,
        11: 1.19,
        12: 0.75,
    }
    weights = np.array([month_weights[date.month] for date in calendar], dtype=float)
    weights /= weights.sum()
    sampled = rng.choice(calendar, size=n_users, replace=True, p=weights)
    return pd.Series(pd.to_datetime(sampled)).sort_values(ignore_index=True)


def sample_language(country: str, rng: np.random.Generator) -> str:
    return str(choose_weighted(rng, COUNTRY_LANGUAGE_OPTIONS[country]))


def build_users(rng: np.random.Generator) -> pd.DataFrame:
    user_ids = [f"USR{idx:06d}" for idx in range(1, USER_COUNT + 1)]
    registration_dates = sample_registration_dates(rng, USER_COUNT)
    acquisition_probs = np.array(list(ACQUISITION_WEIGHTS.values()), dtype=float)
    acquisition_probs /= acquisition_probs.sum()
    country_probs = np.array(list(COUNTRY_WEIGHTS.values()), dtype=float)
    country_probs /= country_probs.sum()
    channels = rng.choice(list(ACQUISITION_WEIGHTS.keys()), size=USER_COUNT, p=acquisition_probs)
    countries = rng.choice(list(COUNTRY_WEIGHTS.keys()), size=USER_COUNT, p=country_probs)
    devices = [str(choose_weighted(rng, DEVICE_WEIGHTS_BY_CHANNEL[channel])) for channel in channels]
    ages = [str(choose_weighted(rng, AGE_WEIGHTS_BY_CHANNEL[channel])) for channel in channels]
    experiences = [
        str(rng.choice(EXPERIENCE_LEVELS, p=EXPERIENCE_WEIGHTS_BY_CHANNEL[channel]))
        for channel in channels
    ]
    languages = [sample_language(country, rng) for country in countries]

    records: list[dict[str, Any]] = []
    for user_id, reg_date, country, channel, device, language, age, experience in zip(
        user_ids,
        registration_dates,
        countries,
        channels,
        devices,
        languages,
        ages,
        experiences,
    ):
        country_quality = COUNTRY_QUALITY_ADJUSTMENT[country]
        skill = EXPERIENCE_SCORE[experience] + country_quality * 0.30 + AGE_QUALITY[age] + rng.normal(0.0, 0.36)
        discipline = EXPERIENCE_SCORE[experience] * 0.40 + CHANNEL_DISCIPLINE[channel] + AGE_QUALITY[age] * 0.70 + rng.normal(0.0, 0.33)
        engagement = CHANNEL_ENGAGEMENT[channel] + (0.10 if device == "desktop" else -0.04 if device == "mobile" else 0.02) + rng.normal(0.0, 0.38)
        risk_bias = CHANNEL_RISK[channel] + AGE_RISK[age] - EXPERIENCE_SCORE[experience] * 0.20 + rng.normal(0.0, 0.36)
        compliance = country_quality + (0.14 if channel in {"direct", "community"} else 0.0) - (0.12 if channel == "influencers" else 0.0) + rng.normal(0.0, 0.25)
        price_sensitivity = (
            0.22
            + (0.18 if channel in {"paid_social", "influencers"} else 0.0)
            + (0.11 if country in {"Brazil", "Mexico", "India", "Nigeria", "Pakistan", "Philippines"} else 0.0)
            - EXPERIENCE_SCORE[experience] * 0.08
            + rng.normal(0.0, 0.14)
        )
        records.append(
            {
                "user_id": user_id,
                "registration_date": reg_date,
                "country": country,
                "acquisition_channel": channel,
                "device_type": device,
                "platform_language": language,
                "age_bucket": age,
                "prior_trading_experience": experience,
                "_skill": skill,
                "_discipline": discipline,
                "_engagement": engagement,
                "_risk_bias": risk_bias,
                "_compliance": compliance,
                "_price_sensitivity": price_sensitivity,
            }
        )

    return pd.DataFrame(records)


def build_kyc_events(users: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for user in users.to_dict("records"):
        registration_date = pd.Timestamp(user["registration_date"])
        start_score = (
            0.42
            + user["_engagement"] * 0.95
            + user["_discipline"] * 0.30
            + (0.16 if user["acquisition_channel"] in {"direct", "community"} else 0.0)
            - (0.13 if user["device_type"] == "mobile" else 0.0)
        )
        kyc_start_prob = float(np.clip(sigmoid(start_score), 0.42, 0.97))

        if rng.random() > kyc_start_prob:
            records.append(
                {
                    "user_id": user["user_id"],
                    "kyc_started_at": pd.NaT,
                    "kyc_completed_at": pd.NaT,
                    "kyc_status": "not_started",
                }
            )
            continue

        started_at = registration_date + pd.Timedelta(days=int(rng.integers(0, 10))) + pd.Timedelta(hours=int(rng.integers(1, 20)))
        verified_score = 1.35 + user["_compliance"] * 1.10 + user["_discipline"] * 0.28 - (0.12 if user["device_type"] == "mobile" else 0.0)
        verified_prob = float(np.clip(sigmoid(verified_score), 0.55, 0.95))
        rejected_prob = float(np.clip(0.03 + max(-user["_compliance"], 0) * 0.10 + (0.03 if user["acquisition_channel"] == "affiliates" else 0.0), 0.02, 0.18))
        pending_prob = float(np.clip(0.02 + (0.05 if registration_date.month == 12 else 0.0), 0.02, 0.10))
        abandonment_prob = max(0.02, 1.0 - verified_prob - rejected_prob - pending_prob)
        outcome = choose_weighted(
            rng,
            {
                "verified": verified_prob,
                "rejected": rejected_prob,
                "pending": pending_prob,
                "abandoned": abandonment_prob,
            },
        )

        if outcome == "verified":
            completed_at = started_at + pd.Timedelta(days=int(rng.integers(1, 8))) + pd.Timedelta(hours=int(rng.integers(1, 23)))
        elif outcome == "rejected":
            completed_at = started_at + pd.Timedelta(days=int(rng.integers(1, 6)))
        else:
            completed_at = pd.NaT

        records.append(
            {
                "user_id": user["user_id"],
                "kyc_started_at": started_at,
                "kyc_completed_at": completed_at,
                "kyc_status": outcome,
            }
        )

    return pd.DataFrame(records)


def purchase_probability(user: dict[str, Any]) -> float:
    score = (
        -1.08
        + user["_skill"] * 0.48
        + user["_engagement"] * 0.62
        + user["_discipline"] * 0.20
        - user["_price_sensitivity"] * 0.70
    )
    if user["acquisition_channel"] == "paid_social":
        score -= 0.08
    elif user["acquisition_channel"] == "community":
        score += 0.14
    elif user["acquisition_channel"] == "direct":
        score += 0.18
    elif user["acquisition_channel"] == "influencers":
        score += 0.03

    if user["registration_date"].month in {1, 9, 11}:
        score += 0.10

    return float(np.clip(sigmoid(score), 0.04, 0.58))


def choose_challenge_type(
    user: dict[str, Any],
    attempt_number: int,
    previous_outcome: str | None,
    rng: np.random.Generator,
) -> str:
    weights = CHALLENGE_TYPE_WEIGHTS[user["prior_trading_experience"]].copy()

    if user["acquisition_channel"] in {"paid_social", "influencers"}:
        weights["low_cost_trial"] += 0.10
        weights["aggressive"] += 0.05
    if user["acquisition_channel"] in {"direct", "community"}:
        weights["swing"] += 0.07
        weights["standard"] += 0.05
    if user["country"] in {"Brazil", "Mexico", "India", "Nigeria", "Pakistan", "Philippines"}:
        weights["low_cost_trial"] += 0.08
    if user["age_bucket"] in {"45-54", "55+"}:
        weights["swing"] += 0.05
        weights["aggressive"] -= 0.03
    if user["_risk_bias"] > 0.35:
        weights["aggressive"] += 0.08
    if user["_risk_bias"] < -0.10:
        weights["swing"] += 0.04

    if attempt_number > 1:
        weights["standard"] += 0.08
        weights["low_cost_trial"] -= 0.05

    if previous_outcome == "phase_1_failed":
        weights["standard"] += 0.05
        weights["low_cost_trial"] += 0.02
        weights["aggressive"] -= 0.05
    elif previous_outcome == "phase_2_failed":
        weights["standard"] += 0.04
        weights["swing"] += 0.04
    elif previous_outcome == "funded_no_payout":
        weights["swing"] += 0.05

    return str(choose_weighted(rng, weights))


def choose_product(
    challenge_type: str,
    user: dict[str, Any],
    rng: np.random.Generator,
) -> dict[str, Any]:
    products = CHALLENGE_PRODUCTS[challenge_type]
    if challenge_type == "low_cost_trial":
        weights = {0: 0.74, 1: 0.26}
    elif challenge_type == "standard":
        weights = {0: 0.34, 1: 0.39, 2: 0.27}
    elif challenge_type == "aggressive":
        weights = {0: 0.30, 1: 0.37, 2: 0.33}
    else:
        weights = {0: 0.23, 1: 0.45, 2: 0.32}

    if user["prior_trading_experience"] == "advanced":
        if len(products) >= 3:
            weights[len(products) - 1] += 0.08
            weights[0] -= 0.05
    if user["_price_sensitivity"] > 0.30:
        weights[0] += 0.10
        weights[len(products) - 1] -= 0.08

    selected_index = int(choose_weighted(rng, weights))
    return products[selected_index]


def choose_promo_code(user: dict[str, Any], rng: np.random.Generator) -> str | None:
    if rng.random() > PROMO_WEIGHTS[user["acquisition_channel"]]:
        return None

    promo_weights = {
        "WELCOME10": 0.31,
        "SPRING15": 0.19,
        "FLASH20": 0.13,
        "COMMUNITY5": 0.17,
        "AFFPARTNER": 0.20,
    }
    if user["acquisition_channel"] == "community":
        promo_weights["COMMUNITY5"] += 0.18
    if user["acquisition_channel"] == "affiliates":
        promo_weights["AFFPARTNER"] += 0.25
    if user["acquisition_channel"] in {"paid_social", "influencers"}:
        promo_weights["FLASH20"] += 0.08
    if user["registration_date"].month in {1, 9, 11}:
        promo_weights["SPRING15"] += 0.06

    return str(choose_weighted(rng, promo_weights))


def build_trader_behavior(
    user: dict[str, Any],
    primary_challenge_type: str,
    rng: np.random.Generator,
) -> dict[str, Any]:
    challenge_duration_adjustment = {
        "standard": 0.0,
        "aggressive": -7.0,
        "swing": 18.0,
        "low_cost_trial": -5.0,
    }
    challenge_risk_adjustment = {
        "standard": 0.0,
        "aggressive": 0.28,
        "swing": -0.06,
        "low_cost_trial": 0.10,
    }

    avg_daily_sessions = float(np.clip(1.35 + user["_engagement"] * 0.72 + user["_discipline"] * 0.20 + rng.normal(0.0, 0.30), 0.2, 5.0))
    avg_trade_duration = float(
        np.clip(
            33.0
            + challenge_duration_adjustment[primary_challenge_type]
            + user["_discipline"] * 13.0
            - user["_risk_bias"] * 9.0
            + rng.normal(0.0, 7.0),
            4.0,
            160.0,
        )
    )
    avg_risk_per_trade = float(
        np.clip(
            0.72
            + challenge_risk_adjustment[primary_challenge_type]
            + user["_risk_bias"] * 0.52
            - user["_skill"] * 0.10
            + rng.normal(0.0, 0.16),
            0.10,
            2.60,
        )
    )
    avg_win_rate = float(np.clip(0.43 + user["_skill"] * 0.07 + user["_discipline"] * 0.03 - user["_risk_bias"] * 0.02 + rng.normal(0.0, 0.04), 0.24, 0.76))
    avg_rr = float(np.clip(1.05 + user["_skill"] * 0.22 + user["_discipline"] * 0.12 - user["_risk_bias"] * 0.07 + rng.normal(0.0, 0.15), 0.55, 2.50))
    max_drawdown_pct = float(
        np.clip(
            5.2
            + user["_risk_bias"] * 2.9
            - user["_discipline"] * 1.8
            - user["_skill"] * 0.8
            + rng.normal(0.0, 1.4),
            1.0,
            22.0,
        )
    )
    violations_lambda = max(0.06, 0.95 + user["_risk_bias"] * 1.15 - user["_discipline"] * 0.65 + (0.22 if primary_challenge_type == "aggressive" else 0.0))
    rule_violations_count = int(min(12, rng.poisson(violations_lambda)))
    inactivity_days = int(
        np.clip(
            round(
                7.0
                - user["_engagement"] * 4.4
                - user["_skill"] * 1.0
                + user["_price_sensitivity"] * 2.2
                + (3.5 if primary_challenge_type == "low_cost_trial" else 0.0)
                + rng.normal(0.0, 3.0)
            ),
            0,
            55,
        )
    )

    return {
        "user_id": user["user_id"],
        "avg_daily_sessions": round(avg_daily_sessions, 2),
        "avg_trade_duration_minutes": round(avg_trade_duration, 1),
        "avg_risk_per_trade_pct": round(avg_risk_per_trade, 2),
        "avg_win_rate": round(avg_win_rate, 3),
        "avg_rr": round(avg_rr, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "rule_violations_count": rule_violations_count,
        "inactivity_days_after_purchase": inactivity_days,
    }


def choose_failure_reason(behavior: dict[str, Any], phase: str, rng: np.random.Generator) -> str:
    weights = {
        "max_drawdown": 0.30 + behavior["max_drawdown_pct"] / 25,
        "daily_loss_limit": 0.20 + behavior["avg_risk_per_trade_pct"] / 4,
        "consistency_rule": 0.18 + max(0.55 - behavior["avg_win_rate"], 0),
        "rule_violation": 0.10 + behavior["rule_violations_count"] / 8,
        "inactivity": 0.08 + behavior["inactivity_days_after_purchase"] / 25,
    }
    if phase == "phase_2":
        weights["consistency_rule"] += 0.06
        weights["inactivity"] += 0.03
    return str(choose_weighted(rng, weights))


def simulate_challenge_progress(
    challenge_id: str,
    purchase_date: pd.Timestamp,
    challenge_type: str,
    account_size: int,
    user: dict[str, Any],
    behavior: dict[str, Any],
    attempt_number: int,
    rng: np.random.Generator,
) -> tuple[dict[str, Any], str]:
    phase1_score = (
        -0.58
        + user["_skill"] * 1.15
        + user["_discipline"] * 0.80
        + user["_engagement"] * 0.32
        - user["_risk_bias"] * 0.55
        + CHALLENGE_DIFFICULTY[challenge_type]
        + (0.10 if user["acquisition_channel"] in {"direct", "community"} else 0.0)
        - (0.12 if user["acquisition_channel"] in {"paid_social", "influencers"} else 0.0)
        + (behavior["avg_win_rate"] - 0.45) * 2.6
        + (behavior["avg_rr"] - 1.05) * 0.65
        - (behavior["avg_risk_per_trade_pct"] - 0.75) * 0.70
        - behavior["rule_violations_count"] * 0.06
        - behavior["inactivity_days_after_purchase"] * 0.03
        - max(behavior["max_drawdown_pct"] - 8.5, 0) * 0.04
        + (0.08 if attempt_number > 1 else 0.0)
    )
    phase1_pass_prob = float(np.clip(sigmoid(phase1_score), 0.04, 0.82))

    phase1_duration = int(
        np.clip(
            round(
                10
                + account_size / 30_000
                + (6 if challenge_type == "swing" else 0)
                - user["_engagement"] * 2.6
                + rng.normal(0.0, 4.0)
            ),
            3,
            36,
        )
    )
    phase1_terminal = purchase_date + pd.Timedelta(days=phase1_duration)

    if rng.random() > phase1_pass_prob:
        failed_reason = choose_failure_reason(behavior, "phase_1", rng)
        return (
            {
                "challenge_id": challenge_id,
                "phase_1_status": "failed",
                "phase_1_completed_at": phase1_terminal,
                "phase_2_status": "not_reached",
                "phase_2_completed_at": pd.NaT,
                "funded_at": pd.NaT,
                "failed_reason": failed_reason,
                "days_to_fail_or_pass": phase1_duration,
            },
            "phase_1_failed",
        )

    phase2_score = (
        -0.76
        + user["_skill"] * 1.26
        + user["_discipline"] * 0.92
        + user["_engagement"] * 0.24
        - user["_risk_bias"] * 0.46
        + CHALLENGE_DIFFICULTY[challenge_type] * 0.90
        + (0.14 if user["prior_trading_experience"] == "advanced" else 0.0)
        + (behavior["avg_win_rate"] - 0.45) * 2.8
        + (behavior["avg_rr"] - 1.05) * 0.78
        - (behavior["avg_risk_per_trade_pct"] - 0.70) * 0.82
        - behavior["rule_violations_count"] * 0.07
        - behavior["inactivity_days_after_purchase"] * 0.025
        - max(behavior["max_drawdown_pct"] - 8.0, 0) * 0.05
        + (0.10 if attempt_number > 1 else 0.0)
    )
    phase2_pass_prob = float(np.clip(sigmoid(phase2_score), 0.05, 0.74))
    phase2_duration = int(
        np.clip(
            round(
                8
                + account_size / 45_000
                + (5 if challenge_type == "swing" else 0)
                - user["_engagement"] * 1.8
                + rng.normal(0.0, 3.5)
            ),
            4,
            28,
        )
    )
    phase2_terminal = phase1_terminal + pd.Timedelta(days=phase2_duration)

    if rng.random() > phase2_pass_prob:
        failed_reason = choose_failure_reason(behavior, "phase_2", rng)
        return (
            {
                "challenge_id": challenge_id,
                "phase_1_status": "passed",
                "phase_1_completed_at": phase1_terminal,
                "phase_2_status": "failed",
                "phase_2_completed_at": phase2_terminal,
                "funded_at": pd.NaT,
                "failed_reason": failed_reason,
                "days_to_fail_or_pass": phase1_duration + phase2_duration,
            },
            "phase_2_failed",
        )

    funded_at = phase2_terminal + pd.Timedelta(days=int(rng.integers(1, 4)))
    return (
        {
            "challenge_id": challenge_id,
            "phase_1_status": "passed",
            "phase_1_completed_at": phase1_terminal,
            "phase_2_status": "passed",
            "phase_2_completed_at": phase2_terminal,
            "funded_at": funded_at,
            "failed_reason": None,
            "days_to_fail_or_pass": phase1_duration + phase2_duration,
        },
        "funded",
    )


def simulate_payouts(
    payout_sequence_start: int,
    challenge_id: str,
    user_id: str,
    funded_at: pd.Timestamp,
    challenge_type: str,
    account_size: int,
    user: dict[str, Any],
    behavior: dict[str, Any],
    rng: np.random.Generator,
) -> tuple[list[dict[str, Any]], str]:
    payout_score = (
        -0.30
        + user["_skill"] * 0.86
        + user["_discipline"] * 0.38
        - user["_risk_bias"] * 0.12
        + CHALLENGE_PAYOUT_BOOST[challenge_type]
        + (0.10 if user["acquisition_channel"] in {"direct", "community"} else 0.0)
        - (0.10 if user["acquisition_channel"] in {"paid_social", "influencers"} else 0.0)
        + (behavior["avg_win_rate"] - 0.45) * 1.8
        + (behavior["avg_rr"] - 1.05) * 0.45
        - behavior["rule_violations_count"] * 0.08
        - behavior["inactivity_days_after_purchase"] * 0.015
    )
    payout_request_prob = float(np.clip(sigmoid(payout_score), 0.08, 0.85))
    if rng.random() > payout_request_prob:
        return [], "funded_no_payout"

    payout_events = 1
    if rng.random() < np.clip(0.18 + max(user["_skill"], 0) * 0.12 + (0.05 if account_size >= 100_000 else 0.0), 0.05, 0.48):
        payout_events += 1
    if payout_events == 2 and rng.random() < 0.18:
        payout_events += 1

    status_base = {
        "approved": 0.79 + user["_discipline"] * 0.10 + user["_compliance"] * 0.05,
        "under_review": 0.12 + behavior["rule_violations_count"] * 0.02 + max(user["_risk_bias"], 0) * 0.10,
        "rejected": 0.06 + behavior["rule_violations_count"] * 0.02 + max(-user["_compliance"], 0) * 0.08,
    }

    base_pct = {
        "standard": 0.016,
        "aggressive": 0.023,
        "swing": 0.020,
        "low_cost_trial": 0.008,
    }[challenge_type]

    records: list[dict[str, Any]] = []
    best_status = "approved"
    sequence = payout_sequence_start
    for payout_number in range(1, payout_events + 1):
        request_date = funded_at + pd.Timedelta(days=int(rng.integers(10, 30)) + (payout_number - 1) * int(rng.integers(14, 28)))
        payout_amount = float(
            np.clip(
                account_size
                * (
                    base_pct
                    + max(user["_skill"], -0.2) * 0.004
                    + max(user["_discipline"], -0.2) * 0.002
                    + rng.normal(0.0, base_pct * 0.25)
                ),
                account_size * 0.004,
                account_size * 0.060,
            )
        )
        payout_status = str(choose_weighted(rng, status_base))
        if payout_status != "approved":
            best_status = payout_status if best_status == "approved" else best_status

        records.append(
            {
                "payout_id": f"PO{sequence:06d}",
                "challenge_id": challenge_id,
                "user_id": user_id,
                "payout_requested_at": request_date,
                "payout_amount_usd": round(payout_amount, 2),
                "payout_status": payout_status,
            }
        )
        sequence += 1

    if any(record["payout_status"] == "approved" for record in records):
        return records, "funded_with_payout"
    return records, "funded_pending_or_rejected"


def rebuy_probability(
    user: dict[str, Any],
    challenge_type: str,
    final_outcome: str,
    attempt_number: int,
) -> float:
    if attempt_number >= 3:
        return 0.0

    if final_outcome == "phase_1_failed":
        probability = 0.22
    elif final_outcome == "phase_2_failed":
        probability = 0.18
    elif final_outcome == "funded_no_payout":
        probability = 0.08
    elif final_outcome == "funded_pending_or_rejected":
        probability = 0.11
    else:
        probability = 0.04

    if user["acquisition_channel"] in {"affiliates", "influencers"}:
        probability += 0.05
    if user["prior_trading_experience"] == "advanced":
        probability -= 0.04
    if challenge_type == "low_cost_trial":
        probability -= 0.03
    if user["_engagement"] < -0.20:
        probability -= 0.03
    if user["_price_sensitivity"] > 0.35:
        probability += 0.02

    return float(np.clip(probability, 0.01, 0.34))


def generate_case_data(seed: int = RANDOM_SEED) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    users_internal = build_users(rng)
    kyc_events = build_kyc_events(users_internal, rng)
    kyc_lookup = kyc_events.set_index("user_id")

    challenges: list[dict[str, Any]] = []
    challenge_progress: list[dict[str, Any]] = []
    payouts: list[dict[str, Any]] = []
    behavior_records: list[dict[str, Any]] = []
    behavior_seen: set[str] = set()

    challenge_sequence = 1
    payout_sequence = 1

    verified_users = users_internal.merge(kyc_events, on="user_id", how="left")
    verified_users = verified_users.loc[verified_users["kyc_status"] == "verified"].copy()

    for user in verified_users.to_dict("records"):
        if rng.random() > purchase_probability(user):
            continue

        kyc_completed_at = pd.Timestamp(user["kyc_completed_at"])
        purchase_date = kyc_completed_at.normalize() + pd.Timedelta(days=int(rng.integers(1, 22)))
        attempt_number = 1
        previous_outcome: str | None = None
        primary_behavior: dict[str, Any] | None = None

        while True:
            challenge_type = choose_challenge_type(user, attempt_number, previous_outcome, rng)
            product = choose_product(challenge_type, user, rng)
            promo_code = choose_promo_code(user, rng)
            challenge_id = f"CH{challenge_sequence:06d}"

            if primary_behavior is None:
                primary_behavior = build_trader_behavior(user, challenge_type, rng)
                behavior_records.append(primary_behavior)
                behavior_seen.add(user["user_id"])

            challenge_row = {
                "challenge_id": challenge_id,
                "user_id": user["user_id"],
                "purchase_date": purchase_date,
                "challenge_type": challenge_type,
                "price_usd": float(product["price_usd"]),
                "account_size": int(product["account_size"]),
                "promo_code_used": promo_code,
            }
            challenges.append(challenge_row)

            progress_row, progress_outcome = simulate_challenge_progress(
                challenge_id=challenge_id,
                purchase_date=purchase_date,
                challenge_type=challenge_type,
                account_size=int(product["account_size"]),
                user=user,
                behavior=primary_behavior,
                attempt_number=attempt_number,
                rng=rng,
            )
            challenge_progress.append(progress_row)

            final_outcome = progress_outcome
            terminal_date = pd.Timestamp(progress_row["phase_1_completed_at"])
            if progress_row["phase_2_completed_at"] is not pd.NaT and pd.notna(progress_row["phase_2_completed_at"]):
                terminal_date = pd.Timestamp(progress_row["phase_2_completed_at"])
            if pd.notna(progress_row["funded_at"]):
                payout_rows, final_outcome = simulate_payouts(
                    payout_sequence_start=payout_sequence,
                    challenge_id=challenge_id,
                    user_id=user["user_id"],
                    funded_at=pd.Timestamp(progress_row["funded_at"]),
                    challenge_type=challenge_type,
                    account_size=int(product["account_size"]),
                    user=user,
                    behavior=primary_behavior,
                    rng=rng,
                )
                payouts.extend(payout_rows)
                payout_sequence += len(payout_rows)
                terminal_date = pd.Timestamp(progress_row["funded_at"])
                if payout_rows:
                    terminal_date = max(pd.Timestamp(row["payout_requested_at"]) for row in payout_rows)

            previous_outcome = final_outcome
            challenge_sequence += 1

            if rng.random() > rebuy_probability(user, challenge_type, final_outcome, attempt_number):
                break

            attempt_number += 1
            purchase_date = terminal_date.normalize() + pd.Timedelta(days=int(rng.integers(5, 32)))
            if purchase_date > pd.Timestamp("2026-03-31"):
                break

    users_public = users_internal.drop(columns=[column for column in users_internal.columns if column.startswith("_")]).copy()
    challenges_df = pd.DataFrame(challenges).sort_values(["purchase_date", "challenge_id"]).reset_index(drop=True)
    challenge_progress_df = pd.DataFrame(challenge_progress).sort_values("challenge_id").reset_index(drop=True)
    payouts_df = pd.DataFrame(payouts).sort_values(["payout_requested_at", "payout_id"]).reset_index(drop=True)
    trader_behavior_df = pd.DataFrame(behavior_records).sort_values("user_id").reset_index(drop=True)

    validate_data(users_public, kyc_events, challenges_df, challenge_progress_df, payouts_df, trader_behavior_df)

    return {
        "users": users_public,
        "kyc_events": kyc_events,
        "challenges": challenges_df,
        "challenge_progress": challenge_progress_df,
        "payouts": payouts_df,
        "trader_behavior": trader_behavior_df,
    }


def validate_data(
    users: pd.DataFrame,
    kyc_events: pd.DataFrame,
    challenges: pd.DataFrame,
    challenge_progress: pd.DataFrame,
    payouts: pd.DataFrame,
    trader_behavior: pd.DataFrame,
) -> None:
    assert users["user_id"].is_unique, "Users must be unique."
    assert kyc_events["user_id"].is_unique, "KYC events should have one row per user."
    assert challenges["challenge_id"].is_unique, "Challenges must be unique."
    assert challenge_progress["challenge_id"].is_unique, "Challenge progress should have one row per challenge."
    assert payouts["payout_id"].is_unique if not payouts.empty else True, "Payout ids must be unique."
    assert set(challenges["user_id"]).issubset(set(users["user_id"])), "Challenges must map to known users."
    assert set(challenge_progress["challenge_id"]) == set(challenges["challenge_id"]), "Each challenge must have progress."
    assert set(payouts["challenge_id"]).issubset(set(challenges["challenge_id"])) if not payouts.empty else True, "Payouts must map to challenges."
    assert set(trader_behavior["user_id"]).issubset(set(challenges["user_id"])) if not trader_behavior.empty else True, "Behavior rows must map to purchasing users."


def save_case_data(data_frames: dict[str, pd.DataFrame]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in data_frames.items():
        output_path = DATA_DIR / f"{name}.csv"
        frame.to_csv(output_path, index=False)


def main() -> None:
    data_frames = generate_case_data()
    save_case_data(data_frames)


if __name__ == "__main__":
    main()
