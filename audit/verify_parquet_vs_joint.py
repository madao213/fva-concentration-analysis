"""Compare historical EXGRVA Parquet to retained prepared CSV joint matrix.

Adapted from verify_parquet_vs_joint.py. Matching records use five exact
dimension keys. This checks equality of intersecting observations, not
classification design or appropriate choice of industry codes.
"""
import argparse
from pathlib import Path

KEYS = ['EXPORTING_AREA','TIME_PERIOD','EXPORTING_ACTIVITY',
        'VALUE_ADDED_SOURCE_AREA','VALUE_ADDED_SOURCE_ACTIVITY']

def q(s): return '"' + s.replace('"','""') + '"'
def lit(s): return "'" + str(s).replace("'","''") + "'"

def run(parquet: Path, joint: Path, output: Path, tolerance: float=1e-6):
    import duckdb
    for p in [parquet,joint]:
        if not p.is_file(): raise FileNotFoundError(p)
    output.mkdir(parents=True,exist_ok=True)
    con=duckdb.connect()
    con.execute('SET threads=4')
    con.execute('CREATE VIEW original AS SELECT * FROM read_parquet('+lit(parquet)+')')
    con.execute("CREATE VIEW joint AS SELECT * FROM read_csv_auto("+lit(joint)+", header=true, compression='gzip', sample_size=20000)")
    orig={k.upper():k for k, *_ in con.execute('DESCRIBE original').fetchall()}
    jmap={k.upper():k for k, *_ in con.execute('DESCRIBE joint').fetchall()}
    for col in KEYS:
        if col not in orig or col not in jmap: raise ValueError('Missing dimension '+col)
    if 'OBS_VALUE' not in orig or 'OBS_VALUE_USD_MILLION' not in jmap:
        raise ValueError('Required measure columns absent')
    def expr(m,k):
        return ('TRY_CAST('+q(m[k])+' AS INTEGER)' if k=='TIME_PERIOD' else
                'CAST('+q(m[k])+' AS VARCHAR)')
    sel_o=', '.join(expr(orig,k)+' AS '+q(k) for k in KEYS)
    sel_j=', '.join(expr(jmap,k)+' AS '+q(k) for k in KEYS)
    con.execute('CREATE VIEW pa AS SELECT '+sel_o+', TRY_CAST('+q(orig['OBS_VALUE'])+
                ' AS DOUBLE) AS val FROM original')
    con.execute('CREATE VIEW jb AS SELECT '+sel_j+', TRY_CAST('+q(jmap['OBS_VALUE_USD_MILLION'])+
                ' AS DOUBLE) AS val FROM joint')
    for tbl in ['pa','jb']:
        key=', '.join(q(k) for k in KEYS)
        duplicates=con.execute('SELECT COUNT(*) FROM (SELECT '+key+
             ' FROM '+tbl+' GROUP BY '+key+' HAVING COUNT(*)>1)').fetchone()[0]
        if duplicates: raise AssertionError(f'{tbl} has {duplicates} duplicate-key groups')
    predicate=' AND '.join('p.'+q(k)+' IS NOT DISTINCT FROM j.'+q(k) for k in KEYS)
    cols=', '.join('j.'+q(k) for k in KEYS)
    con.execute('CREATE TEMP TABLE matched AS SELECT '+cols+
                ',p.val AS parquet_value,j.val AS joint_value,p.val-j.val AS difference '
                'FROM jb j LEFT JOIN pa p ON '+predicate)
    stats=con.execute(
        'SELECT COUNT(*) AS joint_rows, COUNT(parquet_value) AS matched_nonnull, '
        'COUNT(*)-COUNT(parquet_value) AS missing_or_null, MAX(ABS(difference)) AS max_absolute_difference, '
        'COUNT(*) FILTER (WHERE ABS(difference)>?) AS differences_above_tolerance '
        'FROM matched',[tolerance]).df()
    con.execute('COPY (SELECT * FROM matched WHERE parquet_value IS NULL OR '
                'ABS(difference)>'+str(float(tolerance))+') TO '+
                lit(output/'mismatches.csv')+" (HEADER, DELIMITER ',')")
    stats.to_csv(output/'comparison_summary.csv',index=False)
    print(stats.to_string(index=False))
    return stats

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--parquet',type=Path,required=True)
    p.add_argument('--joint',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('audit_output/parquet_comparison'))
    p.add_argument('--tolerance',type=float,default=1e-6)
    a=p.parse_args();run(a.parquet,a.joint,a.output,a.tolerance)
