"""Independently reconcile an original OECD EXGRVA CSV against the historical Parquet.

Use the *original* EXGRVA_CHN_JPN_USA_1995_2022.csv file, not a later
export, re-generated file, or the 5.376m-cell prepared joint matrix.

The comparison covers every CSV row and every Parquet row; it checks the
selected dimension keys, duplicate keys, missing/extra keys, and OBS_VALUE.
Unlike comparing only the prepared matrix, this also verifies the original
Parquet conversion's full retained row population.

Example:
  python audit/verify_raw_csv_vs_parquet.py \\
    --raw /path/to/EXGRVA_CHN_JPN_USA_1995_2022.csv \\
    --parquet /path/to/Joint_Analysis_1995_2022.parquet \\
    --out audit_output/raw_to_parquet

Requires DuckDB; does not upload either input anywhere.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

KEYS = (
    "DATAFLOW",
    "MEASURE",
    "VALUE_ADDED_SOURCE_AREA",
    "VALUE_ADDED_SOURCE_ACTIVITY",
    "EXPORTING_AREA",
    "EXPORTING_ACTIVITY",
    "UNIT_MEASURE",
    "FREQ",
    "TIME_PERIOD",
    "UNIT_MULT",
)


def fingerprint(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compare(raw: Path, parquet: Path, out: Path, tolerance: float = 1e-9,
            memory: str = "4GB") -> dict:
    import duckdb
    for path in (raw, parquet):
        if not path.is_file():
            raise FileNotFoundError(path)
    if tolerance < 0:
        raise ValueError("tolerance must be nonnegative")
    out.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(out / "audit.duckdb"))
    con.execute("SET threads=4")
    con.execute("SET memory_limit=?", [memory])
    con.execute("SET temp_directory=?", [str(out / "duckdb_tmp")])
    q = lambda name: '"' + name.replace('"', '""') + '"'
    literal = lambda value: "'" + str(value).replace("'", "''") + "'"
    con.execute("CREATE VIEW original AS SELECT * FROM read_csv_auto(" +
                literal(raw) + ", all_varchar=true, header=true, sample_size=200000)")
    con.execute("CREATE VIEW historical AS SELECT * FROM read_parquet(" +
                literal(parquet) + ")")
    schema = {}
    for alias in ("original", "historical"):
        columns = {c[0].upper(): c[0] for c in
                   con.execute("DESCRIBE " + alias).fetchall()}
        missing = sorted(set(KEYS + ("OBS_VALUE",)) - set(columns))
        if missing:
            raise ValueError(f"{alias} is missing required columns: {missing}")
        schema[alias] = columns

    # Only identity columns are normalized; raw measure values remain intact.
    def build_select(alias: str) -> str:
        cols = schema[alias]
        select = []
        for name in KEYS:
            expr = ("TRY_CAST(" + q(cols[name]) + " AS BIGINT)"
                    if name in ("TIME_PERIOD", "UNIT_MULT") else
                    "CAST(" + q(cols[name]) + " AS VARCHAR)")
            select.append(expr + " AS " + q(name))
        select.append("TRY_CAST(" + q(cols["OBS_VALUE"]) +
                      " AS DOUBLE) AS value")
        return "SELECT " + ", ".join(select) + " FROM " + alias

    con.execute("CREATE TABLE csv_rows AS " + build_select("original"))
    con.execute("CREATE TABLE parquet_rows AS " + build_select("historical"))
    stats = {}
    keycols = ",".join(q(k) for k in KEYS)
    for name in ("csv_rows", "parquet_rows"):
        n, nullvals = con.execute(
            f"SELECT COUNT(*), COUNT(*)-COUNT(value) FROM {name}"
        ).fetchone()
        duplicates = con.execute(
            f"SELECT COALESCE(SUM(n-1),0) FROM "
            f"(SELECT COUNT(*) AS n FROM {name} GROUP BY {keycols} HAVING COUNT(*)>1)"
        ).fetchone()[0]
        stats[name] = {"rows": int(n), "invalid_numeric_values": int(nullvals),
                       "duplicate_key_excess_rows": int(duplicates)}
        if nullvals or duplicates:
            raise AssertionError(f"{name}: invalid value or duplicate keys: {stats[name]}")
    join = " AND ".join(f"c.{q(k)} IS NOT DISTINCT FROM p.{q(k)}" for k in KEYS)
    # Full outer join detects rows lost and rows added by conversion.
    con.execute("CREATE TABLE checked AS SELECT " +
                ", ".join(f"COALESCE(c.{q(k)}, p.{q(k)}) AS {q(k)}" for k in KEYS) +
                ", c.value AS csv_value, p.value AS parquet_value, "
                "c.value - p.value AS difference, "
                "c.value IS NOT NULL AS in_csv, p.value IS NOT NULL AS in_parquet "
                "FROM csv_rows c FULL OUTER JOIN parquet_rows p ON " + join)
    row = con.execute(
        "SELECT COUNT(*),"
        " COUNT(*) FILTER(WHERE NOT in_csv),"
        " COUNT(*) FILTER(WHERE NOT in_parquet),"
        " COALESCE(MAX(ABS(difference)),0),"
        " COUNT(*) FILTER(WHERE ABS(difference)>?)"
        " FROM checked", [tolerance]
    ).fetchone()
    stats.update({"joined_rows": int(row[0]),
                  "missing_in_raw_csv": int(row[1]),
                  "missing_in_parquet": int(row[2]),
                  "max_absolute_difference": float(row[3]),
                  "values_outside_tolerance": int(row[4]),
                  "tolerance": tolerance})
    fail = (stats["missing_in_raw_csv"] or stats["missing_in_parquet"] or
            stats["values_outside_tolerance"] or
            stats["csv_rows"]["rows"] != stats["parquet_rows"]["rows"])
    mismatches = (
        "SELECT * FROM checked WHERE NOT in_csv OR NOT in_parquet "
        "OR ABS(difference) > " + str(float(tolerance)) +
        " ORDER BY ABS(difference) DESC NULLS FIRST LIMIT 1000"
    )
    con.execute("COPY (" + mismatches + ") TO " +
                literal(out / "mismatches_sample.csv") + " (HEADER true)")
    stats["passed"] = not bool(fail)
    stats["original_csv_sha256"] = fingerprint(raw)
    stats["historical_parquet_sha256"] = fingerprint(parquet)
    stats["input_note"] = "Inputs were provided locally; hashes identify the exact checked bytes."
    (out / "raw_csv_parquet_verification.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    con.close()
    print(json.dumps(stats, indent=2))
    if fail:
        raise AssertionError("Raw CSV to Parquet verification FAILED; see report and mismatches")
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--parquet", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("audit_output/raw_parquet"))
    parser.add_argument("--tolerance", type=float, default=1e-9)
    parser.add_argument("--memory", default="4GB")
    args = parser.parse_args()
    compare(args.raw, args.parquet, args.out, args.tolerance, args.memory)
