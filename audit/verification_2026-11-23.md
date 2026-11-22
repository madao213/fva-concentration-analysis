# Writing sample verification — 2026-11-23

Manuscript: **Foreign Production Concentration and Economic Security Policy in China, Japan, and the US**, revision **Writing Sample 5(6)** (30 pages).

## Independent numerical check

Principal manuscript benchmarks were recalculated from the retained prepared EXGRVA source-pair matrix, rather than read from the repository's derived HHI summaries. This matrix contains 5,376,000 source-pair records, covering 3 exporters, 16 export industries, 28 years, 80 foreign source areas per exporter and 50 source industries; the analysis yields 1,344 exporter-industry-year observations. Negative cells are set to zero before calculating shares.

| Measure | Recalculated | Manuscript rounded |
| --- | ---: | ---: |
| China equal-weighted joint HHI change | +80.476% | +80.5% |
| Japan equal-weighted joint HHI change | +36.347% | +36.3% |
| US equal-weighted joint HHI change | −5.293% | −5.3% |
| China pooled joint HHI change | +8.615% | +8.6% |
| Japan pooled joint HHI change | +59.751% | +59.8% |
| US pooled joint HHI change | +55.053% | +55.1% |
| Full-sample Pearson, geographic vs source-industry HHI | 0.711158 | 0.711 |
| Full-sample Spearman | 0.183255 | 0.183 |
| Pearson excluding C19 | 0.084573 | 0.085 |
| Spearman excluding C19 | 0.016379 | 0.016 |
| Demeaned exporter-industry Pearson | 0.254921 | 0.255 |
| Between-industry covariance share | 93.922% | 93.9% |
| C19 between-industry contribution / total covariance | 87.427% | 87.4% |
| US equal-weighted HHI change excluding C19 | −10.15% | −10.2% |
| US pooled HHI change excluding C19 | −16.76% | −16.8% |
| China pooled HHI change excluding WXD | −12.21% | −12.2% |
| Japan pooled HHI change excluding WXD | +54.60% | +54.6% |
| US pooled HHI change excluding WXD | +60.66% | +60.7% |

The 16 leave-one-industry-out calculations identify C19 as influential. Removing C19 yields Pearson 0.084573; removing any other single industry leaves Pearson between 0.711149 and 0.756098. Excluding C19 is a sensitivity check rather than the baseline.

### US weighting-gap decomposition

The change in weighted-minus-equal-weighted joint HHI was **+0.0091532475**. The symmetric industry-weight component was **+0.0089212273**, or **97.465%** of the net change, while the joint-HHI component was **+0.0002320202**. C19's nominal FVA weight increased **7.7616% to 21.2960%** and contributed **+0.0114615203** to the gap change; C26's weight decreased **24.1554% to 6.0505%** and contributed **−0.0025231130**. The US pooled decomposition yielded a net change of **+0.003864420**.

China's pooled WXD share increased **3.5053% to 9.9131%**. WXD × B06 rose from **1.0232%** to **5.9998%** of pooled foreign value added and ranked first in **1** manufacturing industry in 1995 versus **11** in 2022.

### C26 source-pair check, 2019

- China: KOR × C26 **8.197%**, TWN × C26 **7.931%**, USA × C26 **3.402%**.
- Japan: CHN × C26 **6.582%**, CHN × G **4.843%**, USA × C26 **2.882%**.
- US: CHN × C26 **6.723%**, CHN × G **4.473%**, MEX × G **3.681%**.

C26 2018–2020 HHIs also agree with Section 4.6 after rounding. China's 2018–2019 geographic, source-industry, and joint HHI were 0.085867→0.078454, 0.147513→0.152971, and 0.023620→0.020793; Japan's 2019–2020 geographic and joint values were 0.116939→0.139527 and 0.012952→0.015875; US geographic and joint were 0.104652→0.094264 and 0.013912→0.011685.

## Official-source spot check

The policy comparison was spot-checked against the 2014 Chinese integrated-circuit guidelines, July 2020 State Council Document No. 8, October 2020 NDRC statement, 2021 Japanese METI semiconductor strategy, 2022 JASM support, METI 2022 trade white paper, 2021 US White House supply-chain review, and October 7, 2022 BIS export-control announcement. The main reported policy details were supported by official sources or indexed official excerpts; see [policy sources](../policy/README.md).

## Limits

This check used the retained prepared historical source matrix, not a fresh download of all raw OECD records, and did not independently reverify every academic citation or model the causes of specific policy choices. Nominal current-USD foreign-value-added weights do not directly measure real productive capacity. Earlier raw/Parquet reconciliation records remain under [audit/reports](reports). No raw OECD dataset or manuscript PDF is distributed in this repository.
