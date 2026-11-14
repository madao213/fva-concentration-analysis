import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import pandas as pd
from analyze import hhi,industry_panel
class TestHHI(unittest.TestCase):
    def test_different_marginals_same_joint(self):
        d=pd.DataFrame([('CHN',2022,'C20','A','X',50),('CHN',2022,'C20','B','Y',50)],
                       columns=['exporter','year','export_industry','source_area','source_industry','value'])
        p=industry_panel(d).iloc[0]
        self.assertAlmostEqual(p.geo_hhi,.5)
        self.assertAlmostEqual(p.industry_hhi,.5)
        self.assertAlmostEqual(p.joint_hhi,.5)
    def test_joint_less_or_equal_marginals(self):
        d=pd.DataFrame([('CHN',2022,'C20','A','X',25),('CHN',2022,'C20','A','Y',25),
                        ('CHN',2022,'C20','B','X',25),('CHN',2022,'C20','B','Y',25)],
                        columns=['exporter','year','export_industry','source_area','source_industry','value'])
        p=industry_panel(d).iloc[0]
        self.assertAlmostEqual(p.geo_hhi,.5)
        self.assertAlmostEqual(p.industry_hhi,.5)
        self.assertAlmostEqual(p.joint_hhi,.25)
if __name__=='__main__':unittest.main()
