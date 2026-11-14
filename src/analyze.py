"""Reconstructed replication analysis for OECD TiVA EXGRVA concentration study.

Input: previously prepared non-domestic source-area x source-industry EXGRVA matrix.
Columns are documented in README. Negative cell values are clipped at zero.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

C = {'EXPORTING_AREA':'exporter','TIME_PERIOD':'year','EXPORTING_ACTIVITY':'export_industry',
     'VALUE_ADDED_SOURCE_AREA':'source_area','VALUE_ADDED_SOURCE_ACTIVITY':'source_industry',
     'OBS_VALUE_USD_MILLION':'value'}
KEYS = ['exporter','year','export_industry']
PAIR = ['source_area','source_industry']
EXPORTERS = ['CHN','JPN','USA']

def read_matrix(path: Path, chunksize: int=250_000) -> pd.DataFrame:
    """Read matrix in chunks to avoid materializing millions of raw cells at once."""
    pieces = []
    for chunk in pd.read_csv(path, usecols=list(C), chunksize=chunksize):
        chunk = chunk.rename(columns=C)
        chunk = chunk.loc[chunk.exporter.isin(EXPORTERS) & chunk.year.between(1995,2022)].copy()
        chunk['value'] = pd.to_numeric(chunk.value, errors='raise').clip(lower=0)
        pieces.append(chunk.groupby(KEYS+PAIR, as_index=False, sort=False)['value'].sum())
    if not pieces: raise ValueError('No input rows found')
    matrix = pd.concat(pieces,ignore_index=True).groupby(KEYS+PAIR,as_index=False,sort=False)['value'].sum()
    if matrix.duplicated(KEYS+PAIR).any(): raise AssertionError('Duplicate cell keys')
    if matrix['value'].isna().any(): raise ValueError('Missing values in input')
    return matrix

def hhi(data: pd.DataFrame, groups: list[str], categories: list[str]) -> pd.DataFrame:
    """HHI of categories grouped within observations. Zero-total groups are NaN."""
    sums = data.groupby(groups+categories,sort=False,as_index=False)['value'].sum()
    sums['denom'] = sums.groupby(groups,sort=False)['value'].transform('sum')
    sums['squared'] = np.where(sums.denom > 0, (sums.value/sums.denom)**2, np.nan)
    return sums.groupby(groups,as_index=False,sort=False)['squared'].sum(min_count=1).rename(columns={'squared':'hhi'})

def industry_panel(matrix: pd.DataFrame) -> pd.DataFrame:
    totals = matrix.groupby(KEYS,as_index=False)['value'].sum().rename(columns={'value':'total_fva'})
    results = totals.copy()
    for name,cats in [('geo_hhi',['source_area']),('industry_hhi',['source_industry']),('joint_hhi',PAIR)]:
        results = results.merge(hhi(matrix,KEYS,cats).rename(columns={'hhi':name}),on=KEYS,validate='one_to_one')
    return results.sort_values(KEYS).reset_index(drop=True)

def annual_panel(matrix:pd.DataFrame, panel:pd.DataFrame)->pd.DataFrame:
    annual = (panel.groupby(['exporter','year'],as_index=False)[['geo_hhi','industry_hhi','joint_hhi']]
              .mean().rename(columns={'geo_hhi':'equal_geo_hhi','industry_hhi':'equal_industry_hhi','joint_hhi':'equal_joint_hhi'}))
    weights=panel.copy()
    weights['share'] = weights.total_fva / weights.groupby(['exporter','year']).total_fva.transform('sum')
    weights['weighted_hhi'] = weights.share*weights.joint_hhi
    weighted=weights.groupby(['exporter','year'],as_index=False).weighted_hhi.sum().rename(columns={'weighted_hhi':'weighted_joint_hhi'})
    pooled=hhi(matrix,['exporter','year'],PAIR).rename(columns={'hhi':'pooled_joint_hhi'})
    clean=hhi(matrix.loc[matrix.source_area.ne('WXD')],['exporter','year'],PAIR).rename(columns={'hhi':'pooled_no_wxd_joint_hhi'})
    w=(matrix.assign(wxd_val=lambda x: x.value.where(x.source_area.eq('WXD'),0))
       .groupby(['exporter','year'],as_index=False)[['value','wxd_val']].sum())
    w['wxd_share']=w.wxd_val / w.value
    annual=(annual.merge(weighted,on=['exporter','year']).merge(pooled,on=['exporter','year'])
           .merge(clean,on=['exporter','year']).merge(w[['exporter','year','wxd_share']],on=['exporter','year']))
    annual['weight_gap'] = annual.weighted_joint_hhi-annual.equal_joint_hhi
    annual['dispersion_gap'] = annual.weighted_joint_hhi-annual.pooled_joint_hhi
    return annual.sort_values(['exporter','year']).reset_index(drop=True)

def percent_change(a,b):return 100*(b/a-1) if a != 0 else np.nan

def endpoint_summary(annual:pd.DataFrame)->pd.DataFrame:
    records=[]
    for e,g in annual.groupby('exporter'):
        a,b=g.set_index('year').loc[[1995,2022]].to_dict('index').values()
        rec={'exporter':e}
        for name in ['equal_geo_hhi','equal_industry_hhi','equal_joint_hhi','weighted_joint_hhi','pooled_joint_hhi','pooled_no_wxd_joint_hhi','wxd_share','weight_gap','dispersion_gap']:
            rec[f'{name}_1995']=a[name];rec[f'{name}_2022']=b[name]
            rec[f'{name}_delta']=b[name]-a[name]
            if name.endswith('_hhi'):rec[f'{name}_pct_change']=percent_change(a[name],b[name])
        records.append(rec)
    return pd.DataFrame(records)

def correlation_table(panel:pd.DataFrame)->pd.DataFrame:
    rows=[]
    def add(label, frame):
        rows.append({'sample':label,'n':len(frame),'pearson':frame.geo_hhi.corr(frame.industry_hhi),
                     'spearman':frame.geo_hhi.corr(frame.industry_hhi,method='spearman')})
    add('All observations',panel)
    for e in EXPORTERS:add(e,panel.loc[panel.exporter.eq(e)])
    restricted=panel.loc[panel.export_industry.ne('C19')]
    add('All observations excluding C19',restricted)
    for e in EXPORTERS:add(e+' excluding C19',restricted.loc[restricted.exporter.eq(e)])
    dm=panel.copy()
    for col in ['geo_hhi','industry_hhi']:
        dm[col] = dm[col]-dm.groupby(['exporter','export_industry'])[col].transform('mean')
    add('Within exporter-industry demeaned',dm)
    return pd.DataFrame(rows)

def robustness(panel:pd.DataFrame)->pd.DataFrame:
    out=[]
    for exporter in EXPORTERS:
        for label,frame in [('baseline',panel),('excluding_C19',panel.loc[panel.export_industry.ne('C19')])]:
            vals=frame.loc[frame.exporter.eq(exporter)].groupby('year').joint_hhi.mean()
            for endpoint,lo,hi in [('1995_vs_2022',vals.loc[1995],vals.loc[2022]),
                                    ('1995_vs_2019',vals.loc[1995],vals.loc[2019]),
                                    ('three_year_endpoints',vals.loc[1995:1997].mean(),vals.loc[2020:2022].mean())]:
                out.append({'exporter':exporter,'sample':label,'comparison':endpoint,'start':lo,'end':hi,'change_pct':percent_change(lo,hi)})
    return pd.DataFrame(out)

def make_figures(annual:pd.DataFrame,panel:pd.DataFrame,output:Path):
    """Paper-aligned plots generated from the CSVs already written by run()."""
    from render_figures import generate
    generate(output.parent)


def run(source:Path, output:Path, make_plots:bool=True):
    output.mkdir(parents=True,exist_ok=True)
    m=read_matrix(source)
    panel=industry_panel(m)
    if len(panel)!=1344 or not (panel.groupby(['exporter','year']).size()==16).all():
        raise ValueError(f'Unexpected coverage: {len(panel)} exporter-industry-year rows; expected 1344 and 16 each exporter/year')
    annual=annual_panel(m,panel)
    frames={'industry_year_hhi.csv':panel,'annual_hhi.csv':annual,'endpoint_summary.csv':endpoint_summary(annual),
            'correlations.csv':correlation_table(panel),'joint_robustness.csv':robustness(panel)}
    for filename,frame in frames.items():frame.to_csv(output/filename,index=False,float_format='%.12g')
    if make_plots:
        figure_dir = output.parent / 'figures'
        figure_dir.mkdir(parents=True, exist_ok=True)
        make_figures(annual,panel,figure_dir)
    print('Created',', '.join(frames),'for',len(panel),'exporter-industry-year observations')
    return frames

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True,help='Path to prepared EXGRVA long matrix .csv.gz')
    p.add_argument('--output',type=Path,default=Path('results'))
    p.add_argument('--no-plots',action='store_true')
    args=p.parse_args();run(args.input,args.output,not args.no_plots)
