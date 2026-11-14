"""Synthetic regression test of the OECD raw-to-prepared transformation."""
import csv
import gzip
import sys
import tempfile
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from prepare_exgrva import prepare, EXPORTERS, EXPORT_INDUSTRIES, SOURCE_INDUSTRIES, SOURCE_AREAS

class PreparationTests(unittest.TestCase):
    def test_scope_definitions(self):
        self.assertEqual(len(EXPORTERS),3)
        self.assertEqual(len(EXPORT_INDUSTRIES),16)
        self.assertEqual(len(SOURCE_INDUSTRIES),50)
        self.assertEqual(len(SOURCE_AREAS),81)
        self.assertEqual(len(set(SOURCE_AREAS)),81)

    def test_filter_round_negative_and_domestic(self):
        columns=['EXPORTING_AREA','TIME_PERIOD','EXPORTING_ACTIVITY',
                 'VALUE_ADDED_SOURCE_AREA','VALUE_ADDED_SOURCE_ACTIVITY',
                 'MEASURE','UNIT_MEASURE','FREQ','OBS_VALUE']
        rows=[
           ['CHN','1995','C26','JPN','C26','EXGRVA','USD','A', '0.0276'],
           ['CHN','1995','C26','WXD','B06','EXGRVA','USD','A','-0.0094'],
           ['CHN','1995','C26','CHN','C26','EXGRVA','USD','A','99'],
           ['CHN','1995','_T','JPN','C26','EXGRVA','USD','A','99'],
           ['CHN','1995','C26','JPN','_T','EXGRVA','USD','A','99'],
           ['CHN','1995','C26','JPN','C19','UNRELATED','USD','A','99'],
           ['CHN','1995','C26','JPN','C19','EXGRVA','EUR','A','99'],
           ['CHN','1995','C26','JPN','C19','EXGRVA','USD','Q','99'],
        ]
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);raw=root/'raw.csv';out=root/'prepared.csv.gz'
            with raw.open('w',newline='') as f:
                writer=csv.writer(f);writer.writerow(columns);writer.writerows(rows)
            count,groups=prepare(raw,out,strict=False)
            self.assertEqual((count,groups),(2,1))
            with gzip.open(out,'rt') as f:
                data=list(csv.DictReader(f))
            self.assertEqual(len(data),2)
            vals={(r['VALUE_ADDED_SOURCE_AREA'],r['VALUE_ADDED_SOURCE_ACTIVITY']):
                  float(r['OBS_VALUE_USD_MILLION']) for r in data}
            self.assertAlmostEqual(vals[('JPN','C26')],.028)
            self.assertAlmostEqual(vals[('WXD','B06')],-.009)

if __name__=='__main__': unittest.main()
