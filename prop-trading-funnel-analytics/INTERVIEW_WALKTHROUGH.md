# Mock Interview Walkthrough

Use this file as a short speaking guide for portfolio reviews, recruiter screens, or hiring-manager walkthroughs.

## 1. Two-Minute Case Summary

This case analyzes a challenge-based prop trading funnel from registration through payout. The core point is that conversion quality changes depending on where you measure it. Some channels and trader segments look excellent on registration-to-purchase and funded conversion, but become weak for the business once payout exposure is included.

In the generated sample, the biggest structural breaks are before monetization, especially KYC start and verified-to-purchase conversion. Downstream, `direct` and `community` produce the strongest funded traders, but those same cohorts create the largest payout liability. On product, `low_cost_trial` converts into purchases well but is weak on quality, while `swing` has the strongest funded conversion and the worst economics because payout exposure outgrows fee revenue.

## 2. What I Would Highlight First In An Interview

1. I did not optimize the case around vanity growth metrics.
2. I modeled the funnel at user grain early and challenge grain later, because repeat attempts matter in prop trading.
3. I treated payout exposure as a business-risk metric, not just a finance afterthought.
4. I included behavior features to show how product, growth, and risk can use the same dataset differently.

## 3. Likely Interview Questions

### Why is `paid_social` positive in the gross profit proxy even though the trader quality is weaker?

Because weak funded quality can reduce payout liability. In a prop model, that can make a lower-quality acquisition source look better on short-term economics if the cohort does not survive long enough to generate meaningful payouts.

### Why are `direct` and `community` negative if they bring the best traders?

Because better traders create more real liability. They pass phases, reach funded, and request payouts at much higher rates. That is exactly the trade-off a prop firm has to manage: the best trader cohort is not automatically the best business cohort.

### Why did you include `low_cost_trial`?

It is a common acquisition and monetization product for these platforms. It creates a realistic analytical trap: strong early conversion, weak later quality. That is useful because it forces the analysis away from naive funnel optimization.

### Why use a gross profit proxy instead of full unit economics?

Honestly, because I don't have CAC, payment processing fees, support cost, or hedging data — and making those up would undermine the rest of the analysis. The proxy is limited but honest: it captures whether fee revenue covers payout liability, which is the sharpest version of the trade-off I can show with synthetic data. In a real company I would layer in CAC by channel (which would probably make influencers look even worse) and B-book / A-book routing economics if applicable.

### What would you do next with real production data?

I would add:

- true CAC and affiliate payout data
- challenge-level trading logs
- payout review reasons and fraud flags
- retention and repurchase windows
- hedging or internalization data for funded traders

That would let me separate gross conversion, net revenue quality, and true economic exposure more precisely.

## 4. Phrases Worth Having Ready

These are the points I keep coming back to when explaining the case:

- The best funded cohorts are not automatically the best business cohorts.
- I used payout exposure as a primary KPI rather than a footnote — that framing changes most of the conclusions.
- Low-cost trials inflate top-of-funnel numbers; they should be tracked separately from the core challenge product.
- Some segments look great to growth and bad to finance at the same time. That tension is the point, not a problem to smooth over.

## 5. If Asked About The SQL / Engineering Approach

- The repo runs end-to-end from a single entry point (`python -m src.pipeline`). Data generation, SQL execution, and charting are in separate modules so any piece can be swapped without touching the others.
- SQL uses CTEs throughout — partly for readability, partly because breaking a 200-line query into named stages makes it easier to debug when the numbers look wrong.
- Outputs are written to CSV so the repo can be reviewed without running the pipeline. That matters when sharing with a recruiter who isn't going to set up a DuckDB environment.
- The notebook is a walkthrough layer on top of the pipeline, not the source of truth. I've found that notebooks-as-primary-code tend to get messy fast once you start iterating.
