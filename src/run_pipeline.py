"""Full local OECD EXGRVA -> prepared matrix -> figures/tables pipeline.

Supply original OECD TiVA EXGRVA CSVs/ZIPs or a historical raw Parquet.
The upstream source files and prepared matrix stay local, outside GitHub.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'supplementary'))
sys.path.insert(0,str(ROOT/'audit'))
from prepare_exgrva import prepare
from verify_source_matrix import compare
from analyze import run as analyze
from verify_paper import verify
from generate_paper_tables import generate as tables
from build_supp import generate as supplement
from jpn_c26_decomposition import generate as c26
from verify_joint import run as audit

def sha256(path:Path)->str:
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):digest.update(part)
    return digest.hexdigest()

def execute(source:Path,workspace:Path,reference:Path|None=None):
    workspace=workspace.resolve()
    data=workspace/'data'
    results=workspace/'results'
    data.mkdir(parents=True,exist_ok=True)
    prepared=data/'EXGRVA_Joint_Matrix_Long_1995_2022.csv.gz'
    print('[1/7] Constructing source-area x source-industry matrix')
    n,groups=prepare(source,prepared,strict=True)
    if reference is not None:
        print('[2/7] Comparing against the retained historical reference')
        compare(prepared,reference)
    else:
        print('[2/7] No historical reference supplied; source-cell comparison skipped')
    print('[3/7] Auditing prepared matrix and negative-cell policy')
    audit(prepared,workspace/'audit_output')
    print('[4/7] Calculating HHI, correlations, sensitivities and figures')
    analyze(prepared,results,make_plots=True)
    print('[5/7] Checking numerical values against paper benchmarks')
    verify(results)
    print('[6/7] Building paper Tables 1-4 and supplementary analyses')
    tables(results)
    from analyze import read_matrix
    matrix=read_matrix(prepared)
    supplement(matrix,workspace/'supplementary_output')
    c26(matrix,workspace/'supplementary_output'/'jpn_c26')
    print('[7/7] Recording locally verifiable provenance')
    manifest={
      'created_utc':datetime.now(timezone.utc).isoformat(),
      'source_path':str(source.resolve()),
      'historical_reference_path':str(reference.resolve()) if reference else None,
      'prepared_path':str(prepared),
      'prepared_sha256':sha256(prepared),
      'prepared_rows':int(n),
      'exporter_industry_year_groups':int(groups),
      'paper_benchmarks_checked':True,
      'source_matrix_cell_level_comparison':reference is not None,
      'data_redistributed_in_git':False
    }
    (workspace/'run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('SUCCESS. Local outputs:',workspace)
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True,help='Downloaded OECD EXGRVA CSV/ZIP directory or historical Parquet')
    p.add_argument('--workspace',type=Path,default=Path('local_replication'))
    p.add_argument('--reference',type=Path,help='Optional historical EXGRVA_Joint_Matrix_Long_1995_2022.csv.gz')
    a=p.parse_args();execute(a.source,a.workspace,a.reference)
