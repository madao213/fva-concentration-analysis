"""Exercise full-row CSV/Parquet reconciliation with independent tiny fixtures."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"audit"))
from verify_raw_csv_vs_parquet import compare

COLUMNS=["DATAFLOW","MEASURE","VALUE_ADDED_SOURCE_AREA",
"VALUE_ADDED_SOURCE_ACTIVITY","EXPORTING_AREA","EXPORTING_ACTIVITY",
"UNIT_MEASURE","FREQ","TIME_PERIOD","OBS_VALUE","UNIT_MULT"]

class OriginalRawChecks(unittest.TestCase):
    def write_data(self,base):
        import duckdb
        raw=base/"EXGRVA_CHN_JPN_USA_1995_2022.csv"
        pq=base/"Joint_Analysis_1995_2022.parquet"
        records=[
            ["O","EXGRVA","CHN","C26","JPN","C26","USD","A",1995,"12.5",6],
            ["O","EXGRVA","USA","B06","JPN","C26","USD","A",1995,"-0.0001",6],
            ["O","EXGRVA","JPN","C19","USA","C19","USD","A",2022,"2.125",6],
        ]
        with raw.open("w",newline="") as f:
            w=csv.writer(f);w.writerow(COLUMNS);w.writerows(records)
        c=duckdb.connect()
        c.execute("CREATE TABLE t AS SELECT * FROM read_csv_auto(?,header=true)",[str(raw)])
        c.execute("COPY t TO '"+str(pq)+"' (FORMAT PARQUET)")
        c.close()
        return raw,pq

    def test_identical_conversion_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);raw,pq=self.write_data(base)
            result=compare(raw,pq,base/"audit")
            self.assertTrue(result["passed"])
            self.assertEqual(result["joined_rows"],3)
            self.assertEqual(result["values_outside_tolerance"],0)

    def test_modified_parquet_fails(self):
        import duckdb
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);raw,pq=self.write_data(base)
            c=duckdb.connect()
            c.execute("CREATE TABLE t AS SELECT * FROM read_parquet(?)",[str(pq)])
            c.execute("UPDATE t SET OBS_VALUE=123 WHERE VALUE_ADDED_SOURCE_AREA='CHN'")
            c.execute("COPY t TO '"+str(base/"changed.parquet")+"' (FORMAT PARQUET)")
            c.close()
            with self.assertRaises(AssertionError):
                compare(raw,base/"changed.parquet",base/"audit",tolerance=1e-9)

if __name__=="__main__": unittest.main()
