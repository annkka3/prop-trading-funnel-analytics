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

For a portfolio case, I wanted a metric that is simple, interpretable, and directly tied to the main business tension. In a real company I would extend this to include CAC, payment losses, support cost, hedging, and possibly B-book / A-book routing economics.

### What would you do next with real production data?

I would add:

- true CAC and affiliate payout data
- challenge-level trading logs
- payout review reasons and fraud flags
- retention and repurchase windows
- hedging or internalization data for funded traders

That would let me separate gross conversion, net revenue quality, and true economic exposure more precisely.

## 4. Good One-Liners For Discussion

- “The best funded cohorts are not automatically the best business cohorts.”
- “I treated payout exposure as a first-class KPI, not as a downstream exception.”
- “Low-cost trials are useful acquisition products, but poor proxies for trader quality.”
- “The same segments that look strongest to growth can look riskiest to finance.”

## 5. If Asked About The SQL / Engineering Approach

You can say:

- The repo is fully reproducible from a single pipeline entry point.
- Data generation, SQL, and charting are separated into reusable modules.
- SQL is intentionally readable and business-facing, with CTEs and stage rollups instead of notebook-only logic.
- Outputs are materialized so the repo reads like an internal analytics take-home rather than a scratch project.
