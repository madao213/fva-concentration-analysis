# Geographic, Industrial, and Joint Concentration of Foreign Value Added in Manufacturing Exports

This repository contains the code and results for my study of foreign value added in manufacturing exports from China, Japan, and the United States between 1995 and 2022. The data come from the OECD Trade in Value Added database, 2025 edition, January 2026 revision. The study uses the EXGRVA measure, which identifies where the value added embodied in exports originated.

## Research question

A country can obtain inputs from many foreign economies while still depending heavily on a small number of foreign industries. The paper asks whether geographic diversification is associated with diversification across the industries that produce this value added.

I measure concentration in three ways.

1. **Geographic concentration** measures how foreign value added is distributed across source economies.
2. **Industry concentration** measures how it is distributed across source industries.
3. **Joint concentration** measures how it is distributed across combinations of source economies and source industries.

All three use the Herfindahl Hirschman Index (HHI). A higher HHI indicates that value added is concentrated in fewer sources.

The analysis covers 16 manufacturing export industries in each of the three countries over 28 years. This gives 1,344 observations at the country, export industry, and year level.

I also compare two ways of summarizing joint concentration across manufacturing industries. The first gives each of the 16 exporting industries equal weight. The second combines their foreign value added before calculating concentration. These two measures answer different questions and need not move together.

## Findings

The change in joint concentration between 1995 and 2022 depends partly on how the exporting industries are combined.

| Exporter | Equal average of industry joint HHIs | Joint HHI after pooling manufacturing |
| --- | ---: | ---: |
| China | +80.5% | +8.6% |
| Japan | +36.3% | +59.8% |
| United States | −5.3% | +55.1% |

Two checks are particularly relevant to the interpretation.

Removing the residual source area WXD changes the direction of China's pooled comparison. Instead of increasing by 8.6%, joint concentration falls by 12.2%.

The geographic and industry HHIs have a Pearson correlation of 0.711 across the full set of observations. When the petroleum industry C19 is excluded, the correlation falls to 0.085. The overall relationship is therefore sensitive to the industries included.

These results describe the distribution of foreign value added. They do not by themselves measure the cost of replacing suppliers or the risk of a supply disruption.

## Data and methods

The data are from [OECD TiVA](https://www.oecd.org/en/topics/sub-issues/trade-in-value-added.html). The specific source is the EXGRVA series in the 2025 edition, revised in January 2026.

The analysis keeps foreign sources of value added and excludes domestic sources. It uses 50 detailed source industry categories and 80 foreign source area categories for each exporter. Each country, export industry, and year has 4,000 possible source pairs.

The prepared dataset contains 5,376,000 source pair records. Small negative values are retained in the prepared data and set to zero when concentration is calculated. This is done before calculating source shares. The main results include WXD, with a separate calculation excluding it.

The original OECD CSV, historical Parquet file, and prepared matrix are not stored in this repository. The code for preparing and analysing them is included. Data definitions and expected columns are described in [data/README.md](data/README.md).

## Reproducing the results

Python 3.10 or later is recommended. Install the required packages from the project directory.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

To reproduce the analysis from the historical Parquet file, place `Joint_Analysis_1995_2022.parquet` in the project directory and run the following command.

```bash
python src/run_pipeline.py \
  --source Joint_Analysis_1995_2022.parquet \
  --workspace local_replication
```

If the original prepared matrix is also available, include it as a reference. This checks every reconstructed source pair against the earlier data.

```bash
python src/run_pipeline.py \
  --source Joint_Analysis_1995_2022.parquet \
  --workspace local_replication \
  --reference EXGRVA_Joint_Matrix_Long_1995_2022.csv.gz
```

The program prepares the data, calculates the concentration measures and correlations, checks the main numerical results, and generates the tables and figures. Outputs are saved in `local_replication/`.

The preparation script also accepts OECD EXGRVA CSV files and ZIP archives. See [src/prepare_exgrva.py](src/prepare_exgrva.py) for the input options.

Readers who only want to view or regenerate the figures can use the summary data already in `results/`.

```bash
python src/render_figures.py
```

## Files

| Location | Contents |
| --- | --- |
| `src/` | Data preparation, HHI calculations, figure generation and checks against the paper |
| `results/` | Industry and annual HHI results, correlations, robustness checks and paper tables |
| `figures/` | The three figures used in the paper |
| `audit/` | Data checks and reports from earlier and recent verification runs |
| `supplementary/` | Source pair rankings, WXD sensitivity and the Japan C26 analysis |
| `tests/` | Small tests for the analysis and data preparation code |

## Verification

The data and results have been checked at each main stage of the analysis.

The recovered original CSV and the historical Parquet each contain 14,784,000 records. A comparison of all 11 fields found no differences between their complete record sets.

The historical Parquet was then used to reconstruct the 5,376,000 records in the prepared matrix. The reconstructed matrix matched the retained version without missing cells or numerical differences.

On November 15, 2026, I ran `src/run_pipeline.py` on the complete historical Parquet on my Mac. All seven stages finished. The checks against the paper passed for 19 reported endpoint values and nine correlation results. The program also generated the four paper tables, three figures and supplementary analyses.

The detailed records are available in [audit/reports](audit/reports). The original data files remain local.

## Citation

If you use the results, please cite the accompanying paper and the OECD TiVA database. Repository citation information is provided in [CITATION.cff](CITATION.cff).
