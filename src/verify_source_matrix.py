"""Compare a newly prepared EXGRVA matrix to the historical retained matrix.

Tests cell-level keys and values; no user-owned OECD source data are uploaded.
"""
from pathlib import Path
import argparse

KEYS=('EXPORTING_AREA','TIME_PERIOD','EXPORTING_ACTIVITY',
      'VALUE_ADDED_SOURCE_AREA','VALUE_ADDED_SOURCE_ACTIVITY')

def compare(generated:Path,reference:Path,tolerance=0.0011):
    import duckdb
    con=duckdb.connect()
    con.execute("SET threads=4")
    con.execute("SET memory_limit='4GB'")
    for alias,source in [('a',generated),('b',reference)]:
        if not source.exists():raise FileNotFoundError(source)
        filepath=str(source).replace("'","''")
        con.execute("CREATE TEMP VIEW "+alias+" AS SELECT "+','.join(
            ["CAST("+x+" AS VARCHAR) AS "+x for x in KEYS])+
            ", TRY_CAST(OBS_VALUE_USD_MILLION AS DOUBLE) AS val "
            "FROM read_csv_auto('"+filepath+"',header=true,compression='gzip')")
    on=' AND '.join('a.'+key+'=b.'+key for key in KEYS)
    report=con.execute("SELECT COUNT(*) AS joined_rows,"
             "COUNT(*) FILTER (WHERE a.val IS NULL OR b.val IS NULL) AS missing,"
             "COALESCE(MAX(ABS(a.val-b.val)),0) AS max_abs_difference,"
             "COUNT(*) FILTER (WHERE ABS(a.val-b.val)>?) AS mismatched "
             "FROM a FULL OUTER JOIN b ON "+on,[tolerance]).fetchone()
    rows,missing,maxdiff,mismatched=report
    print(f'Joined rows: {rows:,}; missing: {missing:,}; max diff: {maxdiff:.8g}; beyond tolerance: {mismatched:,}')
    if rows!=5376000 or missing or mismatched:
        raise AssertionError('New prepared matrix does not match historical reference')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--generated',required=True,type=Path)
    p.add_argument('--reference',required=True,type=Path)
    p.add_argument('--tolerance',type=float,default=0.0011)
    a=p.parse_args();compare(a.generated,a.reference,a.tolerance)
