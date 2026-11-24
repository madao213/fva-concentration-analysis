# Final writing sample check (2026-11-24)

## Manuscript

*Foreign Production Concentration and Economic Security Policy in China, Japan, and the United States*, PDF revision of 2026-11-24 at 06:47, 28 pages.

This check links the final manuscript to the public results in this repository. It follows the [2026-11-23 verification report](verification_2026-11-23.md), which documents an independent recalculation using the retained prepared EXGRVA source-pair matrix. That report describes an earlier 30-page revision and remains unchanged.

## US aggregation sensitivity

Section 4.4 and Appendix C, Table C2, report that the US aggregation reversal was present in 2019, before the 2022 endpoint. The following values come from [`results/annual_hhi.csv`](../results/annual_hhi.csv):

| Measure, all 16 US industries | 1995 | 2019 | Change |
| --- | ---: | ---: | ---: |
| Equal-weighted joint HHI | 0.014409569232 | 0.012819620513 | −11.0% |
| Pooled joint HHI | 0.00701945812512 | 0.00822579302074 | +17.2% |

Table C2 also retains the 1995–2022 comparison for all 16 industries (−5.3% equal-weighted, +55.1% pooled) and the calculation excluding C19 (−10.2% equal-weighted, −16.8% pooled). These values agree with the earlier matrix-based verification at manuscript rounding precision. The 2019 pooled result is recorded in the public annual HHI file even though the robustness CSV reports equal-weighted changes only.

## Final manuscript changes

- Section 2.4 uses Weiss (2014) to discuss public support and cooperation with firms in developing technological capabilities. Its discussion of Farrell and Newman (2019) distinguishes jurisdiction over central network nodes from regulatory authority in general.
- Section 3.6 uses Bown and Wang (2024) to explain why semiconductor fabrication involves specialized suppliers, skilled workers and accumulated experience. C26 remains a broader electronics category, not a direct measure of semiconductor imports or fabrication capacity.
- Section 5.2 notes that industry weights are calculated from foreign value added in current US dollars. The results do not separate energy-price movements from changes in production and sourcing.
- Appendix B states the different calculations used for pooled WXD shares and equal-weighted named-only geographic HHI.
- Sections 4.7.1–4.7.3 retain the country-specific data and policy comparisons while shortening repeated conclusions. Section 4.7.4 draws the cross-country inference without asserting a causal effect of HHI on policy choice.

## Scope of verification

The final PDF was checked for consistency with the listed public results, the existing verification report, and the manuscript's reported tables and discussion. **The original OECD files were not downloaded again, and the full seven-stage pipeline was not rerun for this revision.** The earlier source-matrix audit and official-policy spot checks remain the basis for those verification claims. The repository does not distribute the raw OECD data, historical Parquet or full prepared source-pair matrix.
