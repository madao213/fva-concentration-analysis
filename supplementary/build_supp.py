"""Supplementary source-pair rankings, persistence, WXD and C26 summaries.

Adapted from historical build_supp.py. Results are descriptive and are not
extra claims made by the main paper. Input is the prepared EXGRVA joint matrix.
"""
import argparse
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyze import read_matrix

def generate(matrix:pd.DataFrame,output:Path):
    output.mkdir(parents=True,exist_ok=True)
    cols=['exporter','year','source_area','source_industry']
    frames=[]
    for scope, subset in [('manufacturing',matrix),('C26',matrix.loc[matrix.export_industry.eq('C26')])]:
        pair=subset.groupby(cols,as_index=False)['value'].sum()
        pair['total']=pair.groupby(['exporter','year'])['value'].transform('sum')
        pair=pair.loc[pair.total.gt(0)].copy()
        pair['share']=pair.value / pair.total
        pair['rank']=(pair.groupby(['exporter','year'])['share']
                      .rank(method='first',ascending=False))
        pair['scope']=scope
        frames.append(pair)
    all_pairs=pd.concat(frames,ignore_index=True)
    tops=all_pairs.loc[all_pairs['rank'].le(10)].copy()
    tops.sort_values(['scope','exporter','year','rank']).to_csv(output/'annual_top10_source_pairs.csv',index=False)
    rank_summary=[]
    persistence=[]
    wxd=[]
    for (scope,exporter),group in all_pairs.groupby(['scope','exporter'],sort=True):
        subset=tops.loc[tops.scope.eq(scope)&tops.exporter.eq(exporter)]
        def top_pairs(year):
            d=subset.loc[subset.year.eq(year)]
            return set(zip(d.source_area,d.source_industry))
        start,end=top_pairs(1995),top_pairs(2022)
        rank_summary.append({'scope':scope,'exporter':exporter,'common':len(start&end),
                             'union':len(start|end),'jaccard':len(start&end)/len(start|end)})
        for area,industry in end:
            d=group.loc[group.source_area.eq(area)&group.source_industry.eq(industry)]
            listed=subset.loc[subset.source_area.eq(area)&subset.source_industry.eq(industry)]
            vals=d.set_index('year')['share']
            persistence.append({'scope':scope,'exporter':exporter,'source_area':area,
                'source_industry':industry,'years_in_top10':len(listed),
                'first_top10_year':int(listed.year.min()),
                'share_1995':float(vals.get(1995,0)),'share_2022':float(vals.get(2022,0))})
        for year, sub in group.groupby('year'):
            included=(sub.share**2).sum()
            without=sub.loc[sub.source_area.ne('WXD')]
            den=without.value.sum()
            excluded=((without.value/den)**2).sum() if den>0 else float('nan')
            wxd.append({'scope':scope,'exporter':exporter,'year':year,
                        'joint_hhi':included,'joint_hhi_excluding_wxd':excluded,
                        'wxd_share':sub.loc[sub.source_area.eq('WXD'),'share'].sum()})
    pd.DataFrame(rank_summary).to_csv(output/'top10_endpoint_overlap.csv',index=False)
    pd.DataFrame(persistence).to_csv(output/'top10_persistence.csv',index=False)
    pd.DataFrame(wxd).to_csv(output/'wxd_sensitivity.csv',index=False)
    print(f'Saved supplementary tables to {output}')
    return pd.DataFrame(rank_summary)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('supplementary_output'))
    a=p.parse_args()
    generate(read_matrix(a.input),a.output)
