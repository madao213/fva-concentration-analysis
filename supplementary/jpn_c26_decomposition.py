"""Japan C26: China-origin value-added decomposition by source industry.

Adapted from historical 'jpns c26 china decomposition.py'. This version reads
the prepared joint matrix and omits the older OECD '_T' raw-category audit,
which requires the earlier Parquet. It complements, but does not replace,
the manuscript's distinct China-source share in all foreign value added.
"""
import argparse
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyze import read_matrix

def generate(matrix:pd.DataFrame, output:Path):
    output.mkdir(parents=True,exist_ok=True)
    jpn=matrix.loc[matrix.exporter.eq('JPN')&matrix.export_industry.eq('C26')].copy()
    china=jpn.loc[jpn.source_area.eq('CHN')]
    detail=china.groupby(['year','source_industry'],as_index=False)['value'].sum()
    detail['china_source_total']=detail.groupby('year')['value'].transform('sum')
    detail['share_of_china_source']=detail.value/detail.china_source_total
    detail['rank']=detail.groupby('year').share_of_china_source.rank(method='first',ascending=False)
    totals=jpn.groupby('year',as_index=False)['value'].sum().rename(columns={'value':'foreign_total'})
    annual=(detail.groupby('year').agg(china_source_total=('value','sum'),
               source_industries=('source_industry','nunique'),
               source_industry_hhi=('share_of_china_source',lambda x:float((x*x).sum())))
            .reset_index().merge(totals,on='year'))
    annual['china_share_of_all_foreign_fva']=annual.china_source_total/annual.foreign_total
    detail.sort_values(['year','rank']).to_csv(output/'china_source_industry_detail.csv',index=False)
    annual.to_csv(output/'annual_summary.csv',index=False)
    detail.loc[detail.year.isin([1995,2005,2015,2022]) & detail['rank'].le(10)].sort_values(
        ['year','rank']).to_csv(output/'endpoint_top10.csv',index=False)
    print('1995/2022 China-origin shares within Japan C26 FVA:')
    print(annual.loc[annual.year.isin([1995,2022]),
          ['year','china_share_of_all_foreign_fva']].to_string(index=False))
    return annual

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('supplementary_output/jpn_c26'))
    a=p.parse_args();generate(read_matrix(a.input),a.output)
