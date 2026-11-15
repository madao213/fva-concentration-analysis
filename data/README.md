# Local input data

This public repository deliberately excludes the acquired OECD source CSV and ZIP archives, the historical Parquet, and the full prepared joint-source matrix. See the root [README](../README.md) for the data source, scope and recorded audit.

For a complete local reconstruction, use `src/run_pipeline.py --source PATH --workspace local_replication`. The `--source` argument accepts the historical source Parquet or compatible OECD EXGRVA CSV/ZIP input. Preparation, category mapping and the nonnegative-share calculation are implemented in `src/prepare_exgrva.py` and `src/analyze.py`.

The optional `--reference EXGRVA_Joint_Matrix_Long_1995_2022.csv.gz` compares the reconstructed prepared matrix with the retained historical eight-column matrix. The eight-column prepared format is also accepted directly by analysis scripts that operate on the prepared data.

The public `results/` directory contains aggregate outputs, including the C26 annual HHI values and Figure 5's 2019 source-pair shares at manuscript display precision. These are not a substitute for the original detailed OECD files.

Verify relevant OECD licensing and redistribution conditions before sharing raw source material.
