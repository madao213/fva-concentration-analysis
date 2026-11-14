"""Regenerate paper figures from publicly committed summary CSVs.

This script does not require any restricted upstream OECD input data.
"""
from pathlib import Path
import pandas as pd
from analyze import make_figures

ROOT = Path(__file__).resolve().parent.parent
annual = pd.read_csv(ROOT / "results" / "annual_hhi.csv")
panel = pd.read_csv(ROOT / "results" / "industry_year_hhi.csv")
if len(annual) != 84 or len(panel) != 1344:
    raise ValueError("Unexpected annual or industry-year observation count")
output = ROOT / "figures"
output.mkdir(exist_ok=True)
make_figures(annual, panel, output)
for image in sorted(output.glob("*.png")):
    print(f"{image.relative_to(ROOT)}: {image.stat().st_size:,} bytes")
