"""Independent streaming audit: retained 5,376,000-cell matrix -> published HHI CSVs.

No DuckDB, raw OECD downloads, or in-memory full matrix required. Checks all
retained rows, grouped source shares, negative handling and annual pooled HHI.
"""
from __future__ import annotations
import argparse,csv,gzip,json,collections
from pathlib import Path
import pandas as pd

def validate(matrix_file:Path, results_dir:Path, report:Path):
    groups=[];pooled=collections.defaultdict(lambda:collections.defaultdict(float))
    current=None;values=[];n=negative=0;neg_total=0.0
    def finish(key,records):
        if not records:return
        total=sum(v for area,industry,v in records)
        by_area=collections.defaultdict(float);by_industry=collections.defaultdict(float)
        for area,industry,v in records:
            by_area[area]+=v;by_industry[industry]+=v
        def hh(seq):return sum((v/total)**2 for v in seq)
        groups.append((key[0],int(key[1]),key[2],total,hh(by_area.values()),
                       hh(by_industry.values()),hh(v for _,_,v in records)))
    with gzip.open(matrix_file,'rt',newline='') as stream:
        for d in csv.DictReader(stream):
            k=(d['EXPORTING_AREA'],d['TIME_PERIOD'],d['EXPORTING_ACTIVITY'])
            if current is not None and k!=current:finish(current,values);values=[]
            current=k
            raw=float(d['OBS_VALUE_USD_MILLION']); v=max(0.0,raw)
            n+=1
            if raw<0:negative+=1;neg_total+=raw
            area=d['VALUE_ADDED_SOURCE_AREA'];industry=d['VALUE_ADDED_SOURCE_ACTIVITY']
            values.append((area,industry,v))
            pooled[(k[0],k[1])][(area,industry)]+=v
        finish(current,values)
    panel=pd.DataFrame(groups,columns=['exporter','year','export_industry',
                             'total_fva','geo_hhi','industry_hhi','joint_hhi'])
    expected=pd.read_csv(results_dir/'industry_year_hhi.csv')
    merged=panel.merge(expected,on=['exporter','year','export_industry'],
                       suffixes=('_measured','_expected'),validate='one_to_one')
    cols=['total_fva','geo_hhi','industry_hhi','joint_hhi']
    errors={c:float((merged[c+'_measured']-merged[c+'_expected']).abs().max()) for c in cols}
    annual=[]
    for (country,year),part in panel.groupby(['exporter','year']):
        data=pooled[(country,str(year))];t=sum(data.values())
        nonw=[v for (area,industry),v in data.items() if area!='WXD']
        tw=sum(nonw)
        annual.append((country,year,part.geo_hhi.mean(),part.industry_hhi.mean(),
          part.joint_hhi.mean(),sum((v/t)**2 for v in data.values()),
          sum((v/tw)**2 for v in nonw),1-tw/t))
    annual=pd.DataFrame(annual,columns=['exporter','year','equal_geo_hhi',
       'equal_industry_hhi','equal_joint_hhi','pooled_joint_hhi',
       'pooled_no_wxd_joint_hhi','wxd_share'])
    published=pd.read_csv(results_dir/'annual_hhi.csv')
    merged_annual=annual.merge(published,on=['exporter','year'],
                              suffixes=('_measured','_expected'),validate='one_to_one')
    annual_errors={c:float((merged_annual[c+'_measured']-
                       merged_annual[c+'_expected']).abs().max())
                   for c in annual.columns if c not in ('exporter','year')}
    passed=(n==5376000 and len(panel)==1344 and len(merged)==1344
            and len(merged_annual)==84
            and max(errors.values())<1e-8 and max(annual_errors.values())<1e-8)
    result={'scope':'retained_prepared_matrix_to_published_results',
       'records':n,'observations':len(panel),'negative_cells':negative,
       'negative_total_usd_million':neg_total,
       'max_panel_differences':errors,'max_annual_differences':annual_errors,
       'passed':bool(passed),'raw_oecd_to_prepared_matrix_tested':False}
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not passed:raise AssertionError('Full retained-matrix comparison failed')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--matrix',type=Path,required=True)
    p.add_argument('--results',type=Path,default=Path('results'))
    p.add_argument('--report',type=Path,default=Path('audit_output/retained_matrix_validation.json'))
    a=p.parse_args();validate(a.matrix,a.results,a.report)
