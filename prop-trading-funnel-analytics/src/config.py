from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
SQL_DIR = ROOT_DIR / "sql"
OUTPUT_DIR = ROOT_DIR / "outputs"
NOTEBOOK_DIR = ROOT_DIR / "notebooks"
DB_PATH = DATA_DIR / "prop_trading_funnel.duckdb"

RANDOM_SEED = 2025
USER_COUNT = 18_000
REGISTRATION_START = "2025-01-01"
REGISTRATION_END = "2025-12-31"

ACQUISITION_WEIGHTS = {
    "organic": 0.19,
    "paid_social": 0.26,
    "affiliates": 0.18,
    "influencers": 0.12,
    "direct": 0.11,
    "community": 0.14,
}

COUNTRY_WEIGHTS = {
    "United States": 0.14,
    "United Kingdom": 0.08,
    "Canada": 0.05,
    "Germany": 0.06,
    "Spain": 0.04,
    "France": 0.04,
    "Netherlands": 0.03,
    "Poland": 0.04,
    "Brazil": 0.08,
    "Mexico": 0.05,
    "India": 0.10,
    "Philippines": 0.03,
    "Pakistan": 0.03,
    "Nigeria": 0.04,
    "South Africa": 0.03,
    "United Arab Emirates": 0.03,
    "Turkey": 0.03,
}

COUNTRY_LANGUAGE_OPTIONS = {
    "United States": {"English": 0.96, "Spanish": 0.04},
    "United Kingdom": {"English": 0.98, "Polish": 0.02},
    "Canada": {"English": 0.78, "French": 0.18, "Spanish": 0.04},
    "Germany": {"German": 0.78, "English": 0.22},
    "Spain": {"Spanish": 0.87, "English": 0.13},
    "France": {"French": 0.82, "English": 0.18},
    "Netherlands": {"English": 0.46, "Dutch": 0.54},
    "Poland": {"Polish": 0.74, "English": 0.26},
    "Brazil": {"Portuguese": 0.89, "English": 0.11},
    "Mexico": {"Spanish": 0.84, "English": 0.16},
    "India": {"English": 0.54, "Hindi": 0.46},
    "Philippines": {"English": 0.72, "Tagalog": 0.28},
    "Pakistan": {"English": 0.44, "Urdu": 0.56},
    "Nigeria": {"English": 0.77, "French": 0.03, "Arabic": 0.20},
    "South Africa": {"English": 0.66, "French": 0.05, "Arabic": 0.29},
    "United Arab Emirates": {"English": 0.58, "Arabic": 0.42},
    "Turkey": {"Turkish": 0.83, "English": 0.17},
}

DEVICE_WEIGHTS_BY_CHANNEL = {
    "organic": {"desktop": 0.49, "mobile": 0.43, "tablet": 0.08},
    "paid_social": {"desktop": 0.26, "mobile": 0.68, "tablet": 0.06},
    "affiliates": {"desktop": 0.43, "mobile": 0.50, "tablet": 0.07},
    "influencers": {"desktop": 0.24, "mobile": 0.70, "tablet": 0.06},
    "direct": {"desktop": 0.63, "mobile": 0.31, "tablet": 0.06},
    "community": {"desktop": 0.57, "mobile": 0.36, "tablet": 0.07},
}

AGE_WEIGHTS_BY_CHANNEL = {
    "organic": {"18-24": 0.19, "25-34": 0.38, "35-44": 0.26, "45-54": 0.12, "55+": 0.05},
    "paid_social": {"18-24": 0.31, "25-34": 0.40, "35-44": 0.20, "45-54": 0.07, "55+": 0.02},
    "affiliates": {"18-24": 0.24, "25-34": 0.39, "35-44": 0.24, "45-54": 0.10, "55+": 0.03},
    "influencers": {"18-24": 0.36, "25-34": 0.39, "35-44": 0.17, "45-54": 0.06, "55+": 0.02},
    "direct": {"18-24": 0.10, "25-34": 0.31, "35-44": 0.31, "45-54": 0.19, "55+": 0.09},
    "community": {"18-24": 0.12, "25-34": 0.33, "35-44": 0.30, "45-54": 0.17, "55+": 0.08},
}

EXPERIENCE_LEVELS = ["none", "beginner", "intermediate", "advanced"]

EXPERIENCE_WEIGHTS_BY_CHANNEL = {
    "organic": [0.18, 0.34, 0.30, 0.18],
    "paid_social": [0.31, 0.38, 0.22, 0.09],
    "affiliates": [0.21, 0.34, 0.28, 0.17],
    "influencers": [0.29, 0.39, 0.23, 0.09],
    "direct": [0.09, 0.23, 0.35, 0.33],
    "community": [0.11, 0.24, 0.35, 0.30],
}

EXPERIENCE_SCORE = {
    "none": -0.70,
    "beginner": -0.20,
    "intermediate": 0.30,
    "advanced": 0.75,
}

CHANNEL_QUALITY_ADJUSTMENT = {
    "organic": 0.06,
    "paid_social": -0.15,
    "affiliates": -0.05,
    "influencers": -0.19,
    "direct": 0.18,
    "community": 0.14,
}

COUNTRY_QUALITY_ADJUSTMENT = {
    "United States": 0.08,
    "United Kingdom": 0.10,
    "Canada": 0.11,
    "Germany": 0.09,
    "Spain": 0.01,
    "France": 0.02,
    "Netherlands": 0.14,
    "Poland": 0.12,
    "Brazil": -0.08,
    "Mexico": -0.04,
    "India": -0.07,
    "Philippines": -0.06,
    "Pakistan": -0.08,
    "Nigeria": -0.10,
    "South Africa": -0.01,
    "United Arab Emirates": 0.04,
    "Turkey": -0.02,
}

CHALLENGE_TYPE_WEIGHTS = {
    "none": {"standard": 0.22, "aggressive": 0.18, "swing": 0.05, "low_cost_trial": 0.55},
    "beginner": {"standard": 0.34, "aggressive": 0.20, "swing": 0.08, "low_cost_trial": 0.38},
    "intermediate": {"standard": 0.44, "aggressive": 0.27, "swing": 0.15, "low_cost_trial": 0.14},
    "advanced": {"standard": 0.38, "aggressive": 0.20, "swing": 0.32, "low_cost_trial": 0.10},
}

CHALLENGE_PRODUCTS = {
    "standard": [
        {"account_size": 25_000, "price_usd": 149},
        {"account_size": 50_000, "price_usd": 279},
        {"account_size": 100_000, "price_usd": 499},
    ],
    "aggressive": [
        {"account_size": 25_000, "price_usd": 179},
        {"account_size": 50_000, "price_usd": 319},
        {"account_size": 100_000, "price_usd": 569},
    ],
    "swing": [
        {"account_size": 50_000, "price_usd": 299},
        {"account_size": 100_000, "price_usd": 549},
        {"account_size": 150_000, "price_usd": 799},
    ],
    "low_cost_trial": [
        {"account_size": 10_000, "price_usd": 39},
        {"account_size": 25_000, "price_usd": 59},
    ],
}

PROMO_CODES = ["WELCOME10", "SPRING15", "FLASH20", "COMMUNITY5", "AFFPARTNER"]
