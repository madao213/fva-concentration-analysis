"""Construct the paper's prepared EXGRVA joint matrix from an OECD TiVA export.

Accepted inputs: historical TiVA Parquet, one OECD TiVA CSV/CSV.GZ, a
directory of split OECD CSVs, or a directory of seven extracted OECD ZIPs.
Requires DuckDB. Does not publish or redistribute the input dataset.

Important: the 16 detailed export activities, 50 detailed source industries,
and 81 union source-area codes are deliberately EXPLICIT: do not include
subtotal codes such as _T or overlapping activity categories.

Expected baseline coverage: 3 exporters x 28 years x 16 industries x
80 foreign source areas x 50 source industries = 5,376,000 records.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import tempfile
import zipfile

EXPORTERS = ('CHN','JPN','USA')
EXPORT_INDUSTRIES = tuple("""
C10T12 C13T15 C16 C17_18 C19 C20 C21 C22 C23 C24 C25 C26 C27 C28 C29_30 C31T33
""".split())
SOURCE_INDUSTRIES = tuple("""
A01 A02 A03 B05 B06 B07 B08 B09 C10T12 C13T15 C16 C17_18 C19 C20
C21 C22 C23 C241_2431 C242_2432 C25 C26 C27 C28 C29 C301 C302T309
C31T33 D E F G H49 H50 H51 H52 H53 I J58T60 J61 J62_63 K L M N O P Q R S T
""".split())
SOURCE_AREAS = tuple("""
AGO ARE ARG AUS AUT BEL BGD BGR BLR BRA BRN CAN CHE CHL CHN CIV CMR COD COL CRI
CYP CZE DEU DNK EGY ESP EST FIN FRA GBR GRC HKG HRV HUN IDN IND IRL ISL ISR
ITA JOR JPN KAZ KHM KOR LAO LTU LUX LVA MAR MEX MLT MMR MYS NGA NLD NOR
NZL PAK PER PHL POL PRT ROU RUS SAU SEN SGP STP SVK SVN SWE THA TUN TUR
TWN UKR USA VNM WXD ZAF
""".split())
INPUT_COLS = ('EXPORTING_AREA','TIME_PERIOD','EXPORTING_ACTIVITY',
              'VALUE_ADDED_SOURCE_AREA','VALUE_ADDED_SOURCE_ACTIVITY')

def sql_list(values):
    return '(' + ','.join("'" + str(v).replace("'","''") + "'" for v in values) + ')'

def file_array(files):
    # DuckDB multi-file readers accept SQL list literals, not SQL tuples.
    return '[' + ','.join("'" + str(p).replace("'","''") + "'" for p in files) + ']'

def extract_archives(files:list[Path], directory:Path)->list[Path]:
    extracted=[]
    for archive in files:
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                if member.is_dir() or not member.filename.lower().endswith(('.csv','.csv.gz')):
                    continue
                name=Path(member.filename).name
                dest=directory / (archive.stem+'_'+name)
                with z.open(member) as inp, dest.open('wb') as out:
                    import shutil
                    shutil.copyfileobj(inp,out)
                extracted.append(dest)
    return extracted

def prepare(source:Path, output:Path, strict:bool=True):
    import duckdb
    source=source.resolve()
    if not source.exists(): raise FileNotFoundError(source)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='tiva_oecd_') as temp:
        root=Path(temp)
        if source.is_dir():
            allfiles=sorted(p for p in source.rglob('*') if p.is_file())
        else:
            allfiles=[source]
        csvfiles=[p for p in allfiles if p.name.lower().endswith(('.csv','.csv.gz'))]
        parquet=[p for p in allfiles if p.suffix.lower()=='.parquet']
        zipfiles=[p for p in allfiles if p.suffix.lower()=='.zip']
        csvfiles += extract_archives(zipfiles,root)
        if parquet and csvfiles:
            raise ValueError('Provide either Parquet OR CSV inputs, not both')
        if parquet:
            read="read_parquet("+file_array(parquet)+", union_by_name=true)"
        elif csvfiles:
            read="read_csv_auto("+file_array(csvfiles)+", union_by_name=true, header=true, sample_size=25000)"
        else:
            raise ValueError('No Parquet, CSV, CSV.GZ or ZIP datasets found')
        con=duckdb.connect()
        con.execute("SET threads=4")
        con.execute("SET memory_limit='4GB'")
        con.execute('CREATE TEMP VIEW original AS SELECT * FROM '+read)
        mapping={r[0].upper():r[0] for r in con.execute('DESCRIBE original').fetchall()}
        for col in INPUT_COLS:
            if col not in mapping:
                raise ValueError('Missing expected OECD TiVA dimension '+col+
                                 '. Columns available: '+str(list(mapping)))
        valcol=next((mapping[col] for col in ('OBS_VALUE','OBS_VALUE_USD_MILLION') if col in mapping),None)
        if valcol is None:raise ValueError('Expected OBS_VALUE or OBS_VALUE_USD_MILLION')
        def q(x):return '"'+x.replace('"','""')+'"'
        col=lambda x:q(mapping[x])
        filters=[
          'CAST('+col('EXPORTING_AREA')+' AS VARCHAR) IN '+sql_list(EXPORTERS),
          'TRY_CAST('+col('TIME_PERIOD')+' AS INT) BETWEEN 1995 AND 2022',
          'CAST('+col('EXPORTING_ACTIVITY')+' AS VARCHAR) IN '+sql_list(EXPORT_INDUSTRIES),
          'CAST('+col('VALUE_ADDED_SOURCE_AREA')+' AS VARCHAR) IN '+sql_list(SOURCE_AREAS),
          'CAST('+col('VALUE_ADDED_SOURCE_ACTIVITY')+' AS VARCHAR) IN '+sql_list(SOURCE_INDUSTRIES),
          'CAST('+col('VALUE_ADDED_SOURCE_AREA')+' AS VARCHAR) <> CAST('+col('EXPORTING_AREA')+' AS VARCHAR)',
        ]
        # Historical Parquet has EXGRVA as MEASURE. In the dedicated OECD
        # EXGRVA dataset the value may instead be represented by 'VALU'.
        if 'MEASURE' in mapping:filters.append("CAST("+col('MEASURE')+" AS VARCHAR) IN ('EXGRVA','VALU')")
        if 'UNIT_MEASURE' in mapping:filters.append("CAST("+col('UNIT_MEASURE')+" AS VARCHAR)='USD'")
        if 'FREQ' in mapping:filters.append("CAST("+col('FREQ')+" AS VARCHAR)='A'")
        cond=' AND '.join(filters)
        con.execute('CREATE TEMP TABLE selected AS SELECT '+
            ','.join([
            'CAST('+col('EXPORTING_AREA')+' AS VARCHAR) AS EXPORTING_AREA',
            'CAST('+col('TIME_PERIOD')+' AS VARCHAR) AS TIME_PERIOD',
            'CAST('+col('EXPORTING_ACTIVITY')+' AS VARCHAR) AS EXPORTING_ACTIVITY',
            'CAST('+col('VALUE_ADDED_SOURCE_AREA')+' AS VARCHAR) AS VALUE_ADDED_SOURCE_AREA',
            'CAST('+col('VALUE_ADDED_SOURCE_ACTIVITY')+' AS VARCHAR) AS VALUE_ADDED_SOURCE_ACTIVITY',
            'TRY_CAST('+q(valcol)+' AS DOUBLE) AS OBS_VALUE_USD_MILLION'])+
            ' FROM original WHERE '+cond)
        n,groups,non_null=con.execute(
          'SELECT COUNT(*),COUNT(DISTINCT (EXPORTING_AREA,TIME_PERIOD,EXPORTING_ACTIVITY)),'
          'COUNT(OBS_VALUE_USD_MILLION) FROM selected').fetchone()
        if n!=non_null:raise ValueError('Null or non-numeric EXGRVA values after filtering')
        keys=','.join(INPUT_COLS)
        duplicate_groups=con.execute('SELECT COUNT(*) FROM (SELECT '+keys+
                     ' FROM selected GROUP BY '+keys+' HAVING COUNT(*)>1)').fetchone()[0]
        if duplicate_groups:
            raise ValueError(f'{duplicate_groups} duplicate joint-cell key groups; check aggregate codes and input files')
        if strict and (n!=5376000 or groups!=1344):
            raise ValueError(f'Coverage mismatch: expected 5,376,000 cells, 1,344 groups; got {n:,} cells and {groups} groups')
        # Round only at the end to match the historical prepared matrix's
        # three-decimal USD-million values. Negatives are NOT clipped here.
        # They are clipped at the cell level by analyze.py.
        query=(
          'SELECT EXPORTING_AREA,TIME_PERIOD,EXPORTING_ACTIVITY,'
          'VALUE_ADDED_SOURCE_AREA,VALUE_ADDED_SOURCE_AREA AS SOURCE_AREA_LABEL,'
          'VALUE_ADDED_SOURCE_ACTIVITY,VALUE_ADDED_SOURCE_ACTIVITY AS SOURCE_INDUSTRY_LABEL,'
          'ROUND(OBS_VALUE_USD_MILLION,3) AS OBS_VALUE_USD_MILLION '
          'FROM selected ORDER BY EXPORTING_AREA,TIME_PERIOD,EXPORTING_ACTIVITY,'
          'VALUE_ADDED_SOURCE_AREA,VALUE_ADDED_SOURCE_ACTIVITY'
        )
        outpath=str(output).replace("'","''")
        con.execute("COPY ("+query+") TO '"+outpath+"' (HEADER true, DELIMITER ',', COMPRESSION gzip)")
        print(f'Prepared {n:,} cells in {groups} groups -> {output}')
        print('Note: source area/industry labels are codes; analysis uses codes and values.')
        return n,groups

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True,help='OECD source CSV/ZIP/Parquet or directory of split files')
    p.add_argument('--output',type=Path,default=Path('data/EXGRVA_Joint_Matrix_Long_1995_2022.csv.gz'))
    p.add_argument('--no-strict',action='store_true',help='Skip 5,376,000-row / 1,344-group requirement for synthetic tests')
    a=p.parse_args()
    prepare(a.source,a.output,strict=not a.no_strict)
