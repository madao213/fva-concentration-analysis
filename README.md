# Foreign Production Concentration and Economic Security Policy in China, Japan, and the US

This repository contains the replication code, published-precision results, figures, and data audit records for a study of foreign value added in manufacturing exports and economic security policy. The analysis covers China, Japan, and the United States from 1995 to 2022 using the OECD Trade in Value Added (TiVA) 2025 edition, January 2026 revision, EXGRVA indicator.

## Research question

The study asks how the dimensions used to describe source contributions, aggregation across manufacturing export industries, and the treatment of residual foreign source areas change observed concentration, and how those descriptions relate to the capabilities and constraints identified in semiconductor economic security policy.

Three HHI measures describe the same foreign value added under different groupings.

1. **Geographic HHI** groups origins by source economy.
2. **Source-industry HHI** groups origins by economic activity.
3. **Joint HHI** retains each source economy and source industry pair.

Equal-weighted annual means describe the average of 16 manufacturing export industries. Pooled joint HHI combines their foreign value added before measuring concentration. The distinction changes the national result.

The paper also examines C26, computer, electronic and optical products, against semiconductor policy records. China's July 2020 measures, Japan's June 2021 strategy and subsequent domestic fabrication support, and the 2021–2022 US supply-chain and export-control measures identify production capabilities, investment obstacles, and different policy instruments. [The policy evidence guide](policy/README.md) distinguishes this documentary comparison from the TiVA measures.

## Main quantitative findings

| Exporter | Equal-weighted joint HHI change, 1995–2022 | Pooled joint HHI change, 1995–2022 |
| --- | ---: | ---: |
| China | +80.5% | +8.6% |
| Japan | +36.3% | +59.8% |
| United States | −5.3% | +55.1% |

China's geographic concentration declined while its source-industry concentration increased. The geographic and source-industry HHIs have a Pearson correlation of 0.711 in the full 1,344-observation panel, compared with 0.085 after excluding C19, coke and refined petroleum products. Excluding the residual WXD source area changes China's pooled joint HHI comparison from +8.6% to −12.2%. In the United States, C19's foreign-value-added share increased from 7.76% to 21.30% between 1995 and 2022. The weighted-minus-equal-weighted joint HHI gap rose by 0.0091532, with 97.5% of the net change attributable to changes in industry FVA weights. C19 contributed +0.0114615 and C26 −0.0025231 to that gap change; removing C19 is a sensitivity check, not the baseline.

The C26 comparison is distinct from these long-term manufacturing summaries. **Figure 4** traces its three concentration measures in 2018–2020. **Figure 5** compares the three largest source economy and source industry pairs for each exporter in the common year 2019. For Japan and the United States, 2020 remains the more recent full predecision year in the policy discussion.

The measures describe production origins. Government documents supply evidence about the narrower capabilities that policymakers sought to build, secure, or control.

## Data and calculations

The study uses three exporters, 16 manufacturing export industries, and 28 years, yielding 1,344 exporter-industry-year observations. The prepared source matrix contains 5,376,000 possible joint-source records. It excludes domestic value added and has 80 foreign source area categories, including the residual WXD category, and 50 source industries. Negative source-pair cells are retained in the prepared data and set to zero before calculating HHI shares.

The repository contains **public aggregate results**, not the full OECD raw CSV, historical Parquet, or prepared source-pair matrix. See [data/README.md](data/README.md) for local source formats and the data preparation workflow.

## Reproduce the analysis

Python 3.10 or later is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

To reproduce the seven-stage analysis with a locally held historical Parquet:

```bash
python src/run_pipeline.py \
  --source Joint_Analysis_1995_2022.parquet \
  --workspace local_replication
```

If the original prepared matrix is also held locally, pass it as a reference for source-cell reconciliation:

```bash
python src/run_pipeline.py \
  --source Joint_Analysis_1995_2022.parquet \
  --workspace local_replication \
  --reference EXGRVA_Joint_Matrix_Long_1995_2022.csv.gz
```

The preparation script also accepts relevant OECD EXGRVA CSV and ZIP inputs. The original source files are not redistributed here.

To **regenerate all five public manuscript figures** using only the checked results in this repository:

```bash
python src/render_figures.py
```

The figure renderer uses `results/annual_hhi.csv` for Figures 1 and 3, `results/industry_year_hhi.csv` for Figures 2 and 4, and `results/c26_source_pairs_2019.csv` for Figure 5. Figure 5's public CSV carries the shares at the **two-decimal percentage precision printed in the manuscript**. The source matrix is needed to recover their unrounded shares.

## Repository contents

| Location | Contents |
| --- | --- |
| `src/` | Preparation, calculations, sensitivity checks, four-paper-table generation, and the five-figure renderer |
| `results/` | Public HHI panel, correlations, robustness results, Tables 1–4 and 2019 C26 source-pair display data |
| `figures/` | Figure outputs, including the two C26 vector figures |
| `supplementary/` | Source-pair ranking, persistence, WXD and Japan C26 calculation scripts |
| `policy/README.md` | Policy decisions, official sources and interpretation of the C26 comparison |
| `audit/` | Reconciliation records and local verification reports |
| `tests/` | Small tests for the preparation and analysis scripts |

## Verified reproducibility status

The recovered original OECD CSV and historical Parquet each contained 14,784,000 records. The recorded comparison of all 11 fields found no differences across the full sets. The prepared 5,376,000-record matrix was reconstructed from historical Parquet and matched the retained prepared matrix without missing source pairs or numerical differences.

On November 15, 2026, a full seven-stage run of `src/run_pipeline.py` on the historical Parquet completed successfully on the researcher's Mac. The run checked 19 reported endpoint benchmarks and nine correlation rows, and generated the first three paper figures, Tables 1–4, and supplementary analyses. This verification record predates the later Figure 4 and Figure 5 presentation additions. Those figures now use the checked public C26 annual HHI values and the displayed 2019 source-pair shares.

The [2026-11-23 manuscript verification report](audit/verification_2026-11-23.md) documents a separate recalculation of the principal manuscript statistics from the retained prepared EXGRVA source-pair matrix and a focused review of official policy sources. Earlier raw-data reconciliation records remain in [audit/reports](audit/reports). Large source data stay local.

## Citation

The accompanying writing sample is titled *Foreign Production Concentration and Economic Security Policy in China, Japan, and the US*. The repository's software citation metadata is in [CITATION.cff](CITATION.cff). Cite the OECD TiVA database when using its derived statistics.
