"""Synthetic checks for the two restored supplementary analyses."""
import sys
import unittest
from pathlib import Path
import tempfile
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'supplementary'))
from build_supp import generate as supplementary
from jpn_c26_decomposition import generate as jpn_c26

class SupplementaryTests(unittest.TestCase):
    def setUp(self):
        self.matrix=pd.DataFrame([
            ('JPN',1995,'C26','CHN','C26',4),
            ('JPN',1995,'C26','CHN','B06',1),
            ('JPN',1995,'C26','WXD','B06',5),
            ('JPN',2022,'C26','CHN','C26',6),
            ('JPN',2022,'C26','CHN','B06',3),
            ('JPN',2022,'C26','WXD','B06',1),
            ('CHN',1995,'C26','JPN','C26',5),
            ('CHN',2022,'C26','JPN','C26',6),
            ('USA',1995,'C26','JPN','C26',3),
            ('USA',2022,'C26','JPN','C26',4)
        ],columns=['exporter','year','export_industry','source_area','source_industry','value'])

    def test_jpn_c26_share_denominator(self):
        with tempfile.TemporaryDirectory() as tmp:
            annual=jpn_c26(self.matrix,Path(tmp))
            shares=annual.set_index('year')['china_share_of_all_foreign_fva']
            self.assertAlmostEqual(shares.loc[1995],.5)
            self.assertAlmostEqual(shares.loc[2022],.9)

    def test_supplementary_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary=supplementary(self.matrix,Path(tmp))
            self.assertEqual(set(summary['exporter']),{'CHN','JPN','USA'})
            wxd=pd.read_csv(Path(tmp)/'wxd_sensitivity.csv')
            v=wxd.loc[(wxd.scope=='C26')&(wxd.exporter=='JPN')&(wxd.year==1995),'wxd_share'].iloc[0]
            self.assertAlmostEqual(v,.5)

if __name__=='__main__':
    unittest.main()
