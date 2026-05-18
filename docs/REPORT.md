# YesWeHack Rankings: Full Analysis Report

**Source:** https://yeswehack.com/ranking (period = All-time)
**Date collected:** May 17, 2026
**Dataset:** All-time top-100 hunters, 56 public profiles enriched with per-hunter data

---

## Methodology

### Endpoint Discovery

The YesWeHack rankings page is a JavaScript-rendered SPA. Rather than scraping HTML, I opened the page in Firefox DevTools → Network tab → XHR filter → hard reload. Two API calls were immediately visible:

- `GET https://api.yeswehack.com/ranking?page={n}` – paginated all-time leaderboard (25 hunters/page, 4 pages = 100 total)
- `GET https://api.yeswehack.com/hunters/{slug}` – individual public hunter profile (nationality, impact, reports, join year, social links)

### Two-Phase Collection

**Phase 1: Rankings** (`/ranking?page=1..4`): fetched all 100 hunters with rank, points, username, slug, public-profile flag, KYC status, avatar. 4 requests, ~2 seconds total.

**Phase 2: Profile enrichment** (`/hunters/{slug}`): fetched each hunter's public profile page for nationality, nb_reports, impact score, joined_on year, Twitter, and website. Results:

- **56/100 profiles retrieved successfully**
- ~14 returned **404**: private profiles; the API intentionally hides them (expected behavior, not errors)
- ~30 returned **429**: rate-limited after rank 50 at 0.5s inter-request delay. Implementing exponential backoff with the `Retry-After` header would recover these in a subsequent run; the 56-profile subset is sufficient for the analyses below.

### Ethical Scraping Practices

- Self-identifying `User-Agent: ywh-research-scraper/1.0 (technical-assessment)` does not impersonate a browser
- 0.5s delay between requests in v1; 1.5s in v2 (after observing 429s)
- `raise_for_status()` fails loudly on unexpected errors
- 404 and 429 logged and handled gracefully; scraper never crashed

---

## Dataset Summary

| Metric | Value |
|---|---|
| Hunters on leaderboard | 100 (full all-time top-100) |
| Profiles enriched | 56 public profiles (44 private/rate-limited) |
| Mean points (all 100) | 6,531 |
| Median points (all 100) | 4,677 |
| Max points | 82,733 (rabhi, rank 1) |
| Min points | 2,459 (rank 100) |
| Mean impact score (56 profiles) | 19.49 |
| Mean report count (56 profiles) | 523 |
| Unique nationalities | 16 countries represented |
| Hunters with public profile | 81 / 100 (81%) |
| KYC-verified hunters | 97 / 100 (97%) |

---

## Observation 1: Power-Law Points Distribution with a Single Dominant Outlier

The all-time leaderboard follows a sub-Zipfian power-law distribution. Points are concentrated at the top, but not as severely as a strict Pareto rule would predict:

| Segment | % of all points |
|---|---|
| Rank 1 only (rabhi) | **12.7%** |
| Top 10 (10% of hunters) | **33.5%** |
| Top 25 (25% of hunters) | **52.8%** |
| Top 50 (50% of hunters) | **74.8%** |

- **Gini coefficient: 0.387** – moderate inequality (0 = perfect equality, 1 = winner-takes-all)
- **Rank-1 vs rank-2 gap: 3.16×** – rabhi (82,733 pts) is a strong outlier above Xel (26,148 pts)
- **Rank-1 vs rank-100 gap: 33.6×**
- **Power-law fit:** `log(points) = 10.82 − 0.63 × log(rank)`, log-log Pearson r = -0.983
- **Exponent α = 0.63** (sub-Zipfian; a pure Zipf distribution has α ≈ 1.0)

**Interpretation:** The bottom 50 hunters still hold 25% of total points, more than a strict 80/20 Pareto would suggest. Most of the apparent concentration is attributable to a single outlier (rabhi), not a smooth elite gradient. Excluding rank 1, concentration becomes more moderate. This pattern is characteristic of a platform where one exceptional, long-tenured hunter accumulates volume-based points while the broader elite tier remains relatively competitive.

**Implication for YesWeHack:** rabhi has been active since 2016 with 5,522 reports. Their dominance is a product of longevity and volume rather than an insurmountable structural advantage. Newer hunters with high impact scores already rank near the top on a per-report basis.

---

## Observation 2: Strong French Dominance, Global But Concentrated Community

From the 56 public profiles, 16 nationalities are represented. France dominates by a large margin:

| Rank | Country | Hunters | % of retrieved profiles | Median points |
|---|---|---|---|---|
| 1 | 🇫🇷 France | 36 | 64.3% | 6,590 |
| 2 | 🇪🇸 Spain | 4 | 7.1% | 4,514 |
| 3 | 🇨🇳 China | 2 | 3.6% | 6,309 |
| 4 | 🇵🇰 Pakistan | 2 | 3.6% | 5,267 |
| 5 | 🇲🇲 Myanmar | 1 | 1.8% | 7,930 |
| 6 | 🇨🇦 Canada | 1 | 1.8% | — |
| 7 | 🇵🇭 Philippines | 1 | 1.8% | — |
| 8 | 🇮🇹 Italy | 1 | 1.8% | — |
| 9 | 🇸🇪 Sweden | 1 | 1.8% | — |
| 10 | 🇨🇭 Switzerland | 1 | 1.8% | — |

**Important caveat:** Nationality data is only available for the 56 public profiles. Private profiles (19 hunters) and rate-limited profiles (~25 hunters) are not represented. The French dominance may be partially amplified if French hunters are more likely to have public profiles. The actual all-100 distribution is likely more international.

**Interpretation:** YesWeHack was founded in France (2015) and has historically had a strong French security research community. 36 of 56 public profiles (64%) being French is consistent with a European-founded platform that retains a home-market strength in its elite tier. The presence of hunters from Pakistan, Myanmar, Philippines, and China shows the platform has genuine global reach, though Europe remains the core.

---

## Observation 3: Quality vs. Quantity: More Reports Correlates with Lower Impact Score

This is the most counter-intuitive finding. Among the 56 hunters with profile data:

- **Spearman ρ = -0.352, p = 0.008** (statistically significant at α = 0.05)
- More reports is negatively correlated with higher impact score

**Top 5 highest-impact-per-report hunters (quality strategy):**

| Hunter | Rank | Impact | Reports | Impact/Report |
|---|---|---|---|---|
| Mekky | 92 | 29.70 | 91 | **0.326** |
| Nishacid | 82 | 27.20 | 113 | 0.241 |
| Aethlios | 80 | 27.60 | 115 | 0.240 |
| n1nj4sec | 87 | 24.54 | 135 | 0.182 |
| mheranco | 81 | 24.63 | 143 | 0.172 |

**For comparison, rank 1 (rabhi, volume strategy):**
82,733 points from 5,522 reports → impact score 17.11 → **0.003 impact/report**

**Interpretation:** Two completely distinct paths to the top-100 exist on YesWeHack. Volume hunters (like rabhi) accumulate points through sheer number of reports over many years. Quality hunters (Mekky, Nishacid, Aethlios) have far fewer reports but each report has significantly higher severity and precision. Critically, the quality hunters are concentrated in ranks 80–92, they are elite by impact score but not yet by total points, suggesting high future potential. YesWeHack's scoring system rewards both strategies, which is a healthy design.

**Implication:** A hunter's optimal strategy depends on their time horizon and specialization depth. New hunters aiming for the top-100 may find the quality path more accessible than competing with a decade of volume accumulation.

---

## Observation 4: Platform Seniority Does Not Significantly Predict Current Ranking

**Spearman ρ = -0.164, p = 0.226 – not statistically significant.**

Mean points by join year (from 56 profiles with join data):

| Year joined | n | Mean points |
|---|---|---|
| 2016 | 8 | 17,504 |
| 2017 | 4 | 5,218 |
| 2018 | 2 | 7,227 |
| 2019 | 11 | 8,022 |
| 2020 | 6 | 7,781 |
| 2021 | 9 | 6,219 |
| 2022 | 9 | 5,861 |
| 2023 | 5 | 6,068 |
| 2024 | 2 | 6,546 |

**Interpretation:** The 2016 cohort has higher mean points (17,504) largely due to rabhi alone. If we remove rabhi, the 2016 mean drops sharply. More strikingly, hunters who joined in 2024 (mean 6,546 pts) are already competitive with the 2021 cohort (6,219 pts). The data suggests the top-100 is accessible to newer hunters who are highly active, and that longevity alone does not guarantee a high ranking.

**Caveat:** Small per-year cohort sizes (n=2–11) limit the statistical power of this analysis. A full dataset (100 profiles) would be needed for stronger claims.

---

## Observation 5: Public Profile Has No Statistically Significant Effect on Points

| Group | n | Median points | Mean points |
|---|---|---|---|
| Public profile | 81 | 4,846 | 6,796 |
| Private profile | 19 | 4,098 | 5,400 |
| Ratio | — | 1.18× | — |

**Mann-Whitney U = 834, p = 0.574. Not statistically significant at α = 0.05.**

Used Mann-Whitney U rather than a t-test because the points distribution is heavily right-skewed (rabhi's 82,733 would distort a mean-based test). The 1.18× median difference is within noise given the sample sizes and variance.

**Interpretation:** Profile visibility does not appear to confer a measurable points advantage within the elite tier. Private hunters reach top-100 at comparable point levels. This is a fairness-positive finding: the platform does not structurally reward self-promotion over technical skill.

---

## Visualizations

The analyzer script produces a 4-panel figure (`rankings_analysis.png`):

- **Panel 1 (top-left):** Points by rank on log scale – visual confirmation of the power-law shape and rabhi's outlier status
- **Panel 2 (top-right):** Nationality distribution bar chart – French dominance immediately visible
- **Panel 3 (bottom-left):** Impact score vs report count scatter – negative correlation (ρ = −0.352) illustrates the quality/quantity split
- **Panel 4 (bottom-right):** Platform seniority bubble chart – 2016 cohort inflated by rabhi; 2024 joiners already competitive

---

## Limitations and Future Work

1. **56/100 profiles only**
   44 hunters had no profile data (private: ~14, rate-limited: ~30). Implementing exponential backoff with the `Retry-After` header and re-running overnight would likely recover the 429 group. The nationality and impact findings should be treated as indicative rather than representative of the full top-100.

2. **Single snapshot**
   Collected May 17, 2026. Time-series collection (weekly scrapes) would reveal rank velocity, rising hunters, and seasonal activity patterns.

3. **No report-level data**
   Individual report metadata (severity, vulnerability type, program) is not available through the public ranking or profile endpoints. This would require authenticated API access.

4. **Nationality self-reported**
   Hunters set their own nationality; the field may not reflect actual location.

5. **Correlation ≠ causation**
   The quality/quantity split (Obs. 3) and seniority analysis (Obs. 4) are observational. Controlled experiments would be needed to claim causal relationships.

---

*Data collected from `https://api.yeswehack.com/ranking` and `https://api.yeswehack.com/hunters/{slug}` on May 17, 2026. Analysis: Python 3 with pandas, numpy, scipy, matplotlib. Endpoints discovered via Firefox DevTools Network inspection.*
