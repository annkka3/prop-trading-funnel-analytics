from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

from src.config import DATA_DIR, OUTPUT_DIR


CHANNEL_COLORS = {
    "organic": "#2A9D8F",
    "paid_social": "#E76F51",
    "affiliates": "#F4A261",
    "influencers": "#C8553D",
    "direct": "#264653",
    "community": "#6D597A",
}

CHALLENGE_COLORS = {
    "standard": "#4C78A8",
    "aggressive": "#E45756",
    "swing": "#72B7B2",
    "low_cost_trial": "#F2CF5B",
}

OUTCOME_COLORS = {
    "Approved payout": "#2A9D8F",
    "Funded no payout": "#4C78A8",
    "Phase 2 fail": "#F4A261",
    "Phase 1 fail": "#E76F51",
}


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "users": pd.read_csv(DATA_DIR / "users.csv", parse_dates=["registration_date"]),
        "kyc_events": pd.read_csv(DATA_DIR / "kyc_events.csv", parse_dates=["kyc_started_at", "kyc_completed_at"]),
        "challenges": pd.read_csv(DATA_DIR / "challenges.csv", parse_dates=["purchase_date"]),
        "challenge_progress": pd.read_csv(
            DATA_DIR / "challenge_progress.csv",
            parse_dates=["phase_1_completed_at", "phase_2_completed_at", "funded_at"],
        ),
        "payouts": pd.read_csv(DATA_DIR / "payouts.csv", parse_dates=["payout_requested_at"]),
        "trader_behavior": pd.read_csv(DATA_DIR / "trader_behavior.csv"),
        "overall_funnel": pd.read_csv(OUTPUT_DIR / "overall_funnel.csv"),
        "funnel_by_acquisition_channel": pd.read_csv(OUTPUT_DIR / "funnel_by_acquisition_channel.csv"),
        "funnel_by_challenge_type": pd.read_csv(OUTPUT_DIR / "funnel_by_challenge_type.csv"),
        "funded_payout_analysis": pd.read_csv(OUTPUT_DIR / "funded_payout_analysis.csv"),
        "cohort_analysis_by_registration_month": pd.read_csv(
            OUTPUT_DIR / "cohort_analysis_by_registration_month.csv",
            parse_dates=["registration_month"],
        ),
        "trader_segment_comparison": pd.read_csv(OUTPUT_DIR / "trader_segment_comparison.csv"),
    }


def configure_plot_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.figsize": (12, 7),
            "axes.titlesize": 16,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 9,
            "axes.facecolor": "#FCFBF8",
            "figure.facecolor": "#FCFBF8",
            "axes.edgecolor": "#D9D5CE",
            "grid.color": "#E8E2D8",
            "grid.linewidth": 0.8,
        }
    )


def format_currency(value: float) -> str:
    rounded = int(round(value))
    return f"-${abs(rounded):,}" if rounded < 0 else f"${rounded:,}"


def percentage_formatter(value: float, _: float) -> str:
    return f"{value:.0f}%"


def currency_formatter(value: float, _: float) -> str:
    if abs(value) >= 1000:
        return f"${value/1000:.0f}k"
    return f"${value:.0f}"


def style_axes(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#D9D5CE")
    ax.spines["bottom"].set_color("#D9D5CE")
    ax.grid(axis="y", linestyle="-", alpha=0.7)
    ax.grid(axis="x", visible=False)


def create_funnel_chart(overall_funnel: pd.DataFrame) -> None:
    funnel = overall_funnel.copy()
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = ["#264653", "#2A9D8F", "#4C78A8", "#E9C46A", "#F4A261", "#E76F51", "#C8553D", "#7A4EAB"]
    bars = ax.bar(funnel["stage_name"], funnel["entity_count"], color=colors, alpha=0.94, edgecolor="white", linewidth=1.1)

    for bar, conversion, entity_count in zip(bars, funnel["conversion_from_previous_pct"], funnel["entity_count"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(funnel["entity_count"]) * 0.018,
            f"{int(entity_count):,}\n" + ("Start" if pd.isna(conversion) else f"{conversion:.1f}%"),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_title("Platform Funnel: Registration to Approved Payout")
    ax.set_ylabel("Entity count")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=20)
    style_axes(ax)
    ax.text(
        0.01,
        0.02,
        "User grain through purchase, challenge grain afterward. Labels show conversion from the previous stage.",
        transform=ax.transAxes,
        fontsize=9,
        color="#333333",
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "funnel_stage_chart.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def create_acquisition_conversion_chart(channel_funnel: pd.DataFrame) -> None:
    chart = channel_funnel.sort_values("registrations", ascending=False).copy()
    x = np.arange(len(chart))
    width = 0.24

    fig, ax = plt.subplots(figsize=(13, 7))
    ax2 = ax.twinx()
    ax.bar(x - width, chart["registration_to_purchase_pct"], width=width, color="#4C78A8", label="Registration to purchase")
    ax.bar(x, chart["purchase_to_funded_pct"], width=width, color="#F58518", label="Challenge to funded")
    ax.bar(x + width, chart["funded_to_payout_pct"], width=width, color="#54A24B", label="Funded to payout")
    ax2.plot(
        x,
        chart["gross_profit_proxy_usd"],
        color="#1B1B1B",
        linewidth=2.2,
        marker="o",
        label="Gross profit proxy",
    )

    ax.set_title("Acquisition Channel Quality: Volume Does Not Equal Downstream Quality")
    ax.set_ylabel("Conversion rate (%)")
    ax.yaxis.set_major_formatter(FuncFormatter(percentage_formatter))
    ax2.set_ylabel("Gross profit proxy")
    ax2.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
    ax.set_xticks(x)
    ax.set_xticklabels(chart["acquisition_channel"], rotation=15)
    style_axes(ax)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color("#D9D5CE")
    ax2.grid(False)
    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax.legend(lines_1 + lines_2, labels_1 + labels_2, frameon=True, ncol=2, loc="upper right")
    ax.axhline(0, color="#8F8A80", linewidth=0.8, alpha=0.6)

    for idx, row in chart.iterrows():
        ax2.text(
            idx,
            row["gross_profit_proxy_usd"] + (6000 if row["gross_profit_proxy_usd"] >= 0 else -9000),
            format_currency(row["gross_profit_proxy_usd"]),
            ha="center",
            va="bottom" if row["gross_profit_proxy_usd"] >= 0 else "top",
            fontsize=8,
            color="#222222",
        )

    ax.text(
        0.01,
        0.02,
        "Bars show conversion. The black line makes the business trade-off explicit: high-quality trader channels can still be margin-negative once payout exposure is included.",
        transform=ax.transAxes,
        fontsize=9,
        color="#333333",
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "conversion_by_acquisition_channel.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def create_challenge_type_chart(challenge_funnel: pd.DataFrame) -> None:
    chart = challenge_funnel.sort_values("challenges", ascending=False).copy()
    x = np.arange(len(chart))
    width = 0.24

    fig, ax = plt.subplots(figsize=(12, 7))
    ax2 = ax.twinx()
    ax.bar(x - width, chart["phase_1_pass_rate_pct"], width=width, color="#4C78A8", label="Phase 1 pass")
    ax.bar(x, chart["funded_rate_pct"], width=width, color="#72B7B2", label="Funded rate")
    ax.bar(x + width, chart["payout_rate_pct"], width=width, color="#E45756", label="Payout rate")
    ax2.plot(
        x,
        chart["payout_exposure_to_fee_ratio"],
        color="#1B1B1B",
        linewidth=2.2,
        marker="o",
        label="Exposure to fee ratio",
    )

    ax.set_title("Challenge Type Trade-Off: Entry Conversion vs. Downstream Quality")
    ax.set_ylabel("Rate (%)")
    ax.yaxis.set_major_formatter(FuncFormatter(percentage_formatter))
    ax2.set_ylabel("Exposure / fee ratio")
    ax.set_xticks(x)
    ax.set_xticklabels(chart["challenge_type"], rotation=12)
    style_axes(ax)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color("#D9D5CE")
    ax2.grid(False)
    ax2.axhline(1.0, color="#8F8A80", linewidth=1.0, linestyle="--", alpha=0.8)
    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax.legend(lines_1 + lines_2, labels_1 + labels_2, frameon=True, ncol=2, loc="upper right")

    for idx, ratio in enumerate(chart["payout_exposure_to_fee_ratio"]):
        ax2.text(
            idx,
            ratio + 0.04,
            f"{ratio:.2f}x",
            ha="center",
            va="bottom",
            fontsize=8,
            color="#222222",
        )

    ax.text(
        0.01,
        0.02,
        "Bars show conversion. The black line shows how much payout exposure builds relative to fee revenue, which is the real product trade-off.",
        transform=ax.transAxes,
        fontsize=9,
        color="#333333",
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "conversion_by_challenge_type.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def create_cohort_heatmap(cohorts: pd.DataFrame) -> None:
    heatmap_df = cohorts.copy()
    heatmap_df["registration_month_label"] = heatmap_df["registration_month"].dt.strftime("%Y-%m")
    metric_columns = [
        "kyc_verified_rate_pct",
        "purchase_rate_pct",
        "phase_1_pass_rate_pct",
        "phase_2_pass_rate_pct",
        "funded_rate_pct",
        "payout_rate_pct",
    ]
    metric_labels = ["KYC", "Purchase", "Phase 1", "Phase 2", "Funded", "Payout"]
    matrix = heatmap_df[metric_columns].to_numpy()

    fig, ax = plt.subplots(figsize=(11, 7))
    image = ax.imshow(matrix, cmap="YlGnBu", aspect="auto", vmin=0, vmax=max(25, float(matrix.max())))
    ax.set_title("Cohort Progression Heatmap by Registration Month")
    ax.set_xticks(np.arange(len(metric_labels)))
    ax.set_xticklabels(metric_labels)
    ax.set_yticks(np.arange(len(heatmap_df)))
    ax.set_yticklabels(heatmap_df["registration_month_label"])

    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            ax.text(column, row, f"{matrix[row, column]:.1f}", ha="center", va="center", color="#153243", fontsize=8)

    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("Rate (%)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#D9D5CE")
    ax.spines["bottom"].set_color("#D9D5CE")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "cohort_progression_heatmap.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def create_payout_exposure_chart(funded_payout: pd.DataFrame) -> None:
    chart = funded_payout.sort_values("payout_exposure_usd", ascending=False).head(12).sort_values("payout_exposure_usd")
    colors = ["#E76F51" if value >= chart["payout_exposure_usd"].median() else "#4C78A8" for value in chart["payout_exposure_usd"]]

    fig, ax = plt.subplots(figsize=(13, 7))
    bars = ax.barh(chart["segment_name"], chart["payout_exposure_usd"], color=colors, alpha=0.92)
    ax.set_title("Top Funded Segments by Payout Exposure")
    ax.set_xlabel("Payout exposure (approved + under review USD)")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(FuncFormatter(currency_formatter))
    style_axes(ax)

    for bar, payout_rate, exposure_per_challenge in zip(
        bars,
        chart["payout_rate_pct"],
        chart["exposure_per_funded_challenge_usd"],
    ):
        ax.text(
            bar.get_width() + chart["payout_exposure_usd"].max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{payout_rate:.1f}% payout | {format_currency(exposure_per_challenge)}/funded",
            va="center",
            fontsize=8.5,
        )

    ax.text(
        0.01,
        0.02,
        "High-value funded segments can still be the main source of payout liability, which is why conversion and exposure should be monitored together.",
        transform=ax.transAxes,
        fontsize=9,
        color="#333333",
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "payout_exposure_by_segment.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def derive_user_outcomes(
    challenges: pd.DataFrame,
    challenge_progress: pd.DataFrame,
    payouts: pd.DataFrame,
    trader_behavior: pd.DataFrame,
) -> pd.DataFrame:
    challenge_outcomes = challenges.merge(challenge_progress, on="challenge_id", how="inner")
    approved_payout_users = set(payouts.loc[payouts["payout_status"] == "approved", "user_id"]) if not payouts.empty else set()

    challenge_outcomes["outcome_rank"] = np.select(
        [
            challenge_outcomes["user_id"].isin(approved_payout_users),
            challenge_outcomes["funded_at"].notna(),
            challenge_outcomes["phase_2_status"].eq("failed"),
        ],
        [4, 3, 2],
        default=1,
    )

    best_outcomes = (
        challenge_outcomes.sort_values(["user_id", "outcome_rank", "purchase_date"], ascending=[True, False, True])
        .drop_duplicates("user_id")
        .loc[:, ["user_id", "outcome_rank"]]
    )

    label_map = {
        4: "Approved payout",
        3: "Funded no payout",
        2: "Phase 2 fail",
        1: "Phase 1 fail",
    }
    best_outcomes["outcome_group"] = best_outcomes["outcome_rank"].map(label_map)

    return trader_behavior.merge(best_outcomes[["user_id", "outcome_group"]], on="user_id", how="left")


def create_behavior_outcome_chart(user_outcomes: pd.DataFrame, rng_seed: int = 2025) -> None:
    sample = user_outcomes.dropna(subset=["outcome_group"]).copy()
    if len(sample) > 1300:
        sample = sample.sample(1300, random_state=rng_seed)

    fig, ax = plt.subplots(figsize=(12, 7))
    for outcome_group, group in sample.groupby("outcome_group", sort=False):
        ax.scatter(
            group["avg_risk_per_trade_pct"],
            group["avg_win_rate"],
            s=35 + group["rule_violations_count"] * 8,
            alpha=0.62,
            label=outcome_group,
            color=OUTCOME_COLORS[outcome_group],
            edgecolor="white",
            linewidth=0.4,
        )

    ax.set_title("Trader Behavior vs. Funnel Outcome")
    ax.set_xlabel("Average risk per trade (%)")
    ax.set_ylabel("Average win rate")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.1f}%"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0%}"))
    style_axes(ax)
    ax.axvline(sample["avg_risk_per_trade_pct"].median(), color="#8F8A80", linewidth=0.9, linestyle="--", alpha=0.7)
    ax.axhline(sample["avg_win_rate"].median(), color="#8F8A80", linewidth=0.9, linestyle="--", alpha=0.7)
    ax.legend(frameon=True, ncol=2, loc="lower left")
    ax.text(
        0.01,
        0.02,
        "Bubble size reflects rule violations. Progression tends to cluster around lower risk, higher win rate, and fewer rule breaches.",
        transform=ax.transAxes,
        fontsize=9,
        color="#333333",
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "behavior_vs_funnel_outcomes.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_summary(
    data_frames: dict[str, pd.DataFrame],
) -> None:
    users = data_frames["users"]
    challenges = data_frames["challenges"]
    payouts = data_frames["payouts"]
    overall_funnel = data_frames["overall_funnel"]
    acquisition = data_frames["funnel_by_acquisition_channel"]
    challenge_types = data_frames["funnel_by_challenge_type"]
    funded_payout = data_frames["funded_payout_analysis"]
    segments = data_frames["trader_segment_comparison"]

    registrations = int(users["user_id"].nunique())
    purchasers = int(challenges["user_id"].nunique())
    challenge_count = int(challenges["challenge_id"].nunique())
    funded_count = int(overall_funnel.loc[overall_funnel["stage_name"] == "Funded", "entity_count"].iloc[0])
    payout_count = int(overall_funnel.loc[overall_funnel["stage_name"] == "Approved Payout", "entity_count"].iloc[0])

    best_channel = acquisition.sort_values("gross_profit_proxy_usd", ascending=False).iloc[0]
    weakest_channel = acquisition.sort_values("gross_profit_proxy_usd", ascending=True).iloc[0]
    best_type = challenge_types.sort_values("gross_profit_proxy_usd", ascending=False).iloc[0]
    riskiest_type = challenge_types.sort_values("payout_exposure_usd", ascending=False).iloc[0]
    highest_exposure_segment = funded_payout.sort_values("payout_exposure_usd", ascending=False).iloc[0]
    misleading_segments = segments.loc[segments["misleading_top_funnel_flag"] == 1].sort_values(
        "registration_to_purchase_pct", ascending=False
    )

    payout_exposure_total = float(funded_payout["payout_exposure_usd"].sum())
    approved_payout_total = float(payouts.loc[payouts["payout_status"] == "approved", "payout_amount_usd"].sum()) if not payouts.empty else 0.0
    misleading_line = (
        f"- A misleading top-of-funnel segment is **{misleading_segments.iloc[0]['segment_name']}**, which converts well into purchases but falls behind on gross profit proxy once payout exposure is included."
        if not misleading_segments.empty
        else "- No segment crossed the simple misleading-top-funnel flag in this run, but the spread between purchase conversion and downstream value remains meaningful."
    )

    summary_lines = [
        "# Executive Summary",
        "",
        f"- The synthetic case covers **{registrations:,} registrations**, **{purchasers:,} purchasing users**, and **{challenge_count:,} challenge purchases**.",
        f"- **{funded_count:,} challenges** reach funded status and **{payout_count:,} challenges** record an approved payout.",
        f"- Gross fee revenue is contrasted against **{format_currency(payout_exposure_total)}** of payout exposure and **{format_currency(approved_payout_total)}** of approved payouts.",
        f"- The strongest acquisition channel on the gross profit proxy is **{best_channel['acquisition_channel']}**, while **{weakest_channel['acquisition_channel']}** looks weakest once payout exposure is netted against fee revenue.",
        f"- The most balanced challenge type is **{best_type['challenge_type']}**, while **{riskiest_type['challenge_type']}** carries the largest payout exposure footprint.",
        f"- The top funded exposure segment is **{highest_exposure_segment['segment_name']}**, with **{format_currency(highest_exposure_segment['payout_exposure_usd'])}** of payout exposure and a **{highest_exposure_segment['payout_rate_pct']:.1f}%** payout rate.",
        misleading_line,
        "",
        "## Recommendations",
        "",
        "- Optimize media and partner spend on downstream quality, not registrations or first purchase alone.",
        "- Keep low-cost trials as an acquisition product, but do not treat their top-of-funnel conversion as evidence of trader quality.",
        "- Review high-exposure funded segments with a combined lens: funded rate, payout rate, and payout exposure per funded challenge.",
        "- Use behavior-based monitoring earlier in the lifecycle. Higher risk per trade, lower win rate, and more rule violations are visible before funded status.",
    ]

    (OUTPUT_DIR / "summary.md").write_text("\n".join(summary_lines))


def create_analysis_outputs() -> None:
    configure_plot_style()
    data_frames = load_data()
    create_funnel_chart(data_frames["overall_funnel"])
    create_acquisition_conversion_chart(data_frames["funnel_by_acquisition_channel"])
    create_challenge_type_chart(data_frames["funnel_by_challenge_type"])
    create_cohort_heatmap(data_frames["cohort_analysis_by_registration_month"])
    create_payout_exposure_chart(data_frames["funded_payout_analysis"])
    user_outcomes = derive_user_outcomes(
        challenges=data_frames["challenges"],
        challenge_progress=data_frames["challenge_progress"],
        payouts=data_frames["payouts"],
        trader_behavior=data_frames["trader_behavior"],
    )
    create_behavior_outcome_chart(user_outcomes)
    write_summary(data_frames)


def main() -> None:
    create_analysis_outputs()


if __name__ == "__main__":
    main()
