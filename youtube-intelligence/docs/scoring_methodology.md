# Outlier scoring methodology

**Status:** Iteration 0 decision; existing score behavior retained.

## MVP metric

`creator_relative_ratio = candidate_observed_views / creator_comparable_median_views`

The baseline is calculated from comparable uploads by the same channel, excluding the candidate. At this stage the CLI expects the median and sample size to be supplied by the input. Baseline collection is not implemented.

## Discovery bands

| Ratio | Existing label |
|---:|---|
| Below 3x | ordinary |
| 3x to below 5x | candidate |
| 5x to below 10x | strong |
| 10x or above | exceptional |

These are internal discovery labels, not statistically calibrated probabilities or universal industry thresholds. Preserve them for backward compatibility until benchmark evidence supports a change.

## Comparability requirements

Before a baseline is considered valid, the future baseline builder should:
1. Use the same creator/channel.
2. Separate Shorts and long-form.
3. Exclude the candidate video.
4. Prefer a comparable duration class.
5. Define and record a publication/lookback window.
6. Use a median or another robust statistic rather than a mean vulnerable to viral skew.
7. Record sample size and eligibility exclusions.
8. Flag low sample size; do not fabricate confidence.

## Separate signals

- **Creator-relative ratio:** candidate views divided by creator median views. Primary signal.
- **Views/subscribers:** current views divided by current subscriber count. Reach/context signal, not creator-relative performance.
- **Velocity/VPH:** requires trustworthy time-series or explicitly labelled third-party estimates. Do not infer historical velocity from one current snapshot or calculate a misleading lifetime-views-per-age proxy and call it VPH.

## Interpretation

An outlier is a candidate for qualitative investigation. It does not prove which hook, title, thumbnail or story technique caused success. Topic demand, video age, format, creator growth, distribution, paid promotion, seasonality and external events can confound comparisons.

## Iteration 3 evaluation

Benchmark ratios against known examples and compare median-based baselines with alternatives (trimmed mean, median absolute deviation, percentile rank). Retain the current ratio unless evidence shows a material improvement. Any future score version must be recorded in output and reports.
