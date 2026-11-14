"""Generate manuscript Tables 1--4 from validated, public HHI result CSVs."""
from pathlib import Path
import argparse
import pandas as pd

COUNTRIES={'CHN':'China','JPN':'Japan','USA':'US'}

def generate(directory:Path):
    directory.mkdir(parents=True,exist_ok=True)
    endpoint=pd.read_csv(directory/'endpoint_summary.csv')
    correlation=pd.read_csv(directory/'correlations.csv')
    one=[]
    three=[]
    four=[]
    for _,r in endpoint.iterrows():
        country=COUNTRIES[r.exporter]
        one.append({'Exporter':country,
                    'Geo 1995':r.equal_geo_hhi_1995,
                    'Geo 2022':r.equal_geo_hhi_2022,
                    'Geo change':r.equal_geo_hhi_delta,
                    'Industry 1995':r.equal_industry_hhi_1995,
                    'Industry 2022':r.equal_industry_hhi_2022,
                    'Industry change':r.equal_industry_hhi_delta})
        three.append({'Exporter':country,
                      'Equal 1995':r.equal_joint_hhi_1995,
                      'Equal 2022':r.equal_joint_hhi_2022,
                      'Change (%)':r.equal_joint_hhi_pct_change,
                      'Pooled 1995':r.pooled_joint_hhi_1995,
                      'Pooled 2022':r.pooled_joint_hhi_2022,
                      'Pooled change (%)':r.pooled_joint_hhi_pct_change})
        four.append({'Exporter':country,
                     'Baseline 1995':r.pooled_joint_hhi_1995,
                     'Baseline 2022':r.pooled_joint_hhi_2022,
                     'Change (%)':r.pooled_joint_hhi_pct_change,
                     'Excl. WXD 1995':r.pooled_no_wxd_joint_hhi_1995,
                     'Excl. WXD 2022':r.pooled_no_wxd_joint_hhi_2022,
                     'Excl. WXD change (%)':r.pooled_no_wxd_joint_hhi_pct_change})
    pd.DataFrame(one).to_csv(directory/'paper_table1.csv',index=False)
    correlation.rename(columns={'sample':'Sample','n':'N',
       'pearson':'Pearson','spearman':'Spearman'}).to_csv(directory/'paper_table2.csv',index=False)
    pd.DataFrame(three).to_csv(directory/'paper_table3.csv',index=False)
    pd.DataFrame(four).to_csv(directory/'paper_table4.csv',index=False)
    for i in range(1,5):
        print('Created',directory/f'paper_table{i}.csv')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,default=Path('results'))
    a=p.parse_args();generate(a.results)
