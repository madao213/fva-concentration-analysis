"""Audit retained EXGRVA prepared long matrix. Adapted from historical verify_joint.py.

This checks counts, duplicate keys, negatives and reproduces HHI from retained data.
The input is a prepared matrix, not the original OECD raw download.
"""
import argparse
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from analyze import read_matrix, industry_panel, annual_panel, endpoint_summary

def run(source: Path, output: Path):
    try:
        import duckdb
    except ImportError as exc:
        raise SystemExit('Install duckdb (pip install -r requirements.txt)') from exc
    con = duckdb.connect()
    con.execute('SET threads=4')
    table = "read_csv_auto(?, header=true, compression='gzip', all_varchar=true)"
    summary = (
        "SELECT COUNT(*) AS rows, "
        "COUNT(*) FILTER (WHERE TRY_CAST(OBS_VALUE_USD_MILLION AS DOUBLE)<0) AS negative_cells, "
        "SUM(CASE WHEN TRY_CAST(OBS_VALUE_USD_MILLION AS DOUBLE)<0 "
        "THEN TRY_CAST(OBS_VALUE_USD_MILLION AS DOUBLE) ELSE 0 END) AS negative_total, "
        "COUNT(DISTINCT (EXPORTING_AREA,TIME_PERIOD,EXPORTING_ACTIVITY,"
        "VALUE_ADDED_SOURCE_AREA,VALUE_ADDED_SOURCE_ACTIVITY)) AS unique_keys, "
        "COUNT(DISTINCT (EXPORTING_AREA,TIME_PERIOD,EXPORTING_ACTIVITY)) AS groups "
        "FROM " + table
    )
    stats = con.execute(summary, [str(source)]).df().iloc[0].to_dict()
    size_sql = ("SELECT MIN(n),MAX(n) FROM (SELECT COUNT(*) AS n FROM " + table +
                " GROUP BY EXPORTING_AREA,TIME_PERIOD,EXPORTING_ACTIVITY)")
    low, high = con.execute(size_sql, [str(source)]).fetchone()
    stats.update(min_cells_per_group=low, max_cells_per_group=high)
    if int(stats['rows']) != int(stats['unique_keys']): raise AssertionError('Duplicate source keys found')
    if int(stats['groups']) != 1344: raise AssertionError('Expected 1344 exporter-industry-year groups')
    if (low,high) != (4000,4000): raise AssertionError('Expected 4000 source-pair cells per observation')
    matrix = read_matrix(source)
    panel = industry_panel(matrix)
    annual = annual_panel(matrix,panel)
    if len(panel) != 1344: raise AssertionError('Unexpected HHI panel size')
    output.mkdir(parents=True,exist_ok=True)
    pd.DataFrame([stats]).to_csv(output/'matrix_audit.csv',index=False)
    endpoint_summary(annual).to_csv(output/'verified_endpoints.csv',index=False)
    print(pd.DataFrame([stats]).to_string(index=False))
    print('Saved outputs:',output.resolve())
    return stats

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('audit_output'))
    a=p.parse_args()
    run(a.input,a.output)
