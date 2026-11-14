"""Compare reconstructed results against numerical benchmarks reported in the paper.
Benchmarks are displayed precision only. They are not the input to analysis.
"""
from pathlib import Path
import argparse
import pandas as pd

EXPECTED = {
 ('CHN','equal_geo_hhi_1995'):0.1001,('CHN','equal_geo_hhi_2022'):0.0652,
 ('CHN','equal_industry_hhi_1995'):0.0792,('CHN','equal_industry_hhi_2022'):0.1292,
 ('JPN','equal_geo_hhi_1995'):0.0895,('JPN','equal_geo_hhi_2022'):0.0916,
 ('JPN','equal_industry_hhi_1995'):0.0951,('JPN','equal_industry_hhi_2022'):0.1065,
 ('USA','equal_geo_hhi_1995'):0.0926,('USA','equal_geo_hhi_2022'):0.0872,
 ('USA','equal_industry_hhi_1995'):0.1024,('USA','equal_industry_hhi_2022'):0.0882,
 ('CHN','equal_joint_hhi_pct_change'):80.5,('CHN','pooled_joint_hhi_pct_change'):8.6,
 ('JPN','equal_joint_hhi_pct_change'):36.3,('JPN','pooled_joint_hhi_pct_change'):59.8,
 ('USA','equal_joint_hhi_pct_change'):-5.3,('USA','pooled_joint_hhi_pct_change'):55.1,
 ('CHN','pooled_no_wxd_joint_hhi_pct_change'):-12.2,
}
CORR={
 'All observations':(1344,.711,.183),'CHN':(448,.799,.311),
 'JPN':(448,.677,.136),'USA':(448,.702,.168),
 'All observations excluding C19':(1260,.085,.016),
 'CHN excluding C19':(420,.308,.174),'JPN excluding C19':(420,.037,-.046),
 'USA excluding C19':(420,-.034,-.005),
 'Within exporter-industry demeaned':(1344,.255,.116),
}

def verify(directory:Path):
    endpoints=pd.read_csv(directory/'endpoint_summary.csv').set_index('exporter')
    corr=pd.read_csv(directory/'correlations.csv').set_index('sample')
    errors=[]
    for (exp,col),value in EXPECTED.items():
        found=float(endpoints.loc[exp,col]);tol=.051 if 'pct_change' in col else .000051
        if abs(found-value)>tol:errors.append(f'{exp} {col}: expected ≈{value}, got {found}')
    for sample,(n,p,s) in CORR.items():
        got=corr.loc[sample]
        if int(got['n'])!=n or abs(got['pearson']-p)>.00051 or abs(got['spearman']-s)>.00051:
            errors.append(f'{sample}: expected N={n}, Pearson≈{p}, Spearman≈{s}; got {got.to_dict()}')
    if errors:
        for e in errors: print('FAIL:',e)
        raise SystemExit(1)
    print(f'PASS: {len(EXPECTED)} endpoint benchmarks and {len(CORR)} correlation rows match paper rounding.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--results',type=Path,default=Path('results'))
    args=parser.parse_args();verify(args.results)
