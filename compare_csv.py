#!/usr/bin/env python3
"""Compare two CSV files by Website_or_App_Title and font usage columns."""

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Tuple


KEY_COLUMN = "Website_or_App_Title"
COMPARE_COLUMNS = ("Total_Font_Use", "Unique_Font_Use")


def _read_csv(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header row.")
        missing = [c for c in (KEY_COLUMN, *COMPARE_COLUMNS) if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")
        return list(reader)


def _to_decimal(value: str) -> Optional[Decimal]:
    trimmed = (value or "").strip()
    if not trimmed:
        return None
    try:
        return Decimal(trimmed)
    except InvalidOperation:
        return None


def _index_by_title(rows: List[dict]) -> Dict[str, dict]:
    index: Dict[str, dict] = {}
    for row in rows:
        title = (row.get(KEY_COLUMN) or "").strip()
        if not title:
            continue
        # Keep the first seen title to avoid non-deterministic overwrites.
        index.setdefault(title, row)
    return index


def _compare_rows(left: dict, right: dict) -> Tuple[bool, dict]:
    result = {}
    all_equal = True

    for column in COMPARE_COLUMNS:
        left_raw = (left.get(column) or "").strip()
        right_raw = (right.get(column) or "").strip()

        left_num = _to_decimal(left_raw)
        right_num = _to_decimal(right_raw)

        if left_num is not None and right_num is not None:
            equal = left_num == right_num
            delta = str(right_num - left_num)
        else:
            equal = left_raw == right_raw
            delta = ""

        all_equal = all_equal and equal
        result[f"{column}_left"] = left_raw
        result[f"{column}_right"] = right_raw
        result[f"{column}_equal"] = equal
        result[f"{column}_delta"] = delta

    return all_equal, result


def compare_csvs(left_path: Path, right_path: Path) -> List[dict]:
    left_rows = _read_csv(left_path)
    right_rows = _read_csv(right_path)

    left_by_title = _index_by_title(left_rows)
    right_by_title = _index_by_title(right_rows)

    all_titles = sorted(set(left_by_title) | set(right_by_title))
    comparisons: List[dict] = []

    for title in all_titles:
        left = left_by_title.get(title)
        right = right_by_title.get(title)

        if left is None:
            comparisons.append(
                {
                    KEY_COLUMN: title,
                    "status": "missing_in_left",
                    **{f"{c}_left": "" for c in COMPARE_COLUMNS},
                    **{f"{c}_right": (right.get(c, "") if right else "") for c in COMPARE_COLUMNS},
                    **{f"{c}_equal": False for c in COMPARE_COLUMNS},
                    **{f"{c}_delta": "" for c in COMPARE_COLUMNS},
                }
            )
            continue

        if right is None:
            comparisons.append(
                {
                    KEY_COLUMN: title,
                    "status": "missing_in_right",
                    **{f"{c}_left": (left.get(c, "") if left else "") for c in COMPARE_COLUMNS},
                    **{f"{c}_right": "" for c in COMPARE_COLUMNS},
                    **{f"{c}_equal": False for c in COMPARE_COLUMNS},
                    **{f"{c}_delta": "" for c in COMPARE_COLUMNS},
                }
            )
            continue

        all_equal, detail = _compare_rows(left, right)
        comparisons.append(
            {
                KEY_COLUMN: title,
                "status": "match" if all_equal else "different",
                **detail,
            }
        )

    return comparisons


def _write_output(path: Path, rows: List[dict]) -> None:
    if not rows:
        return
    fieldnames = [KEY_COLUMN, "status"]
    for column in COMPARE_COLUMNS:
        fieldnames.extend(
            [f"{column}_left", f"{column}_right", f"{column}_equal", f"{column}_delta"]
        )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _print_summary(rows: List[dict]) -> None:
    total = len(rows)
    matches = sum(1 for r in rows if r["status"] == "match")
    different = sum(1 for r in rows if r["status"] == "different")
    missing_left = sum(1 for r in rows if r["status"] == "missing_in_left")
    missing_right = sum(1 for r in rows if r["status"] == "missing_in_right")

    print(f"Compared titles: {total}")
    print(f"Matches: {matches}")
    print(f"Differences: {different}")
    print(f"Missing in left CSV: {missing_left}")
    print(f"Missing in right CSV: {missing_right}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare two CSV files by title and font usage columns."
    )
    parser.add_argument("left_csv", type=Path, help="Path to first CSV file")
    parser.add_argument("right_csv", type=Path, help="Path to second CSV file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("comparison_result.csv"),
        help="Output CSV path (default: comparison_result.csv)",
    )
    parser.add_argument(
        "--only-differences",
        action="store_true",
        help="Write only non-match rows to output",
    )
    args = parser.parse_args()

    results = compare_csvs(args.left_csv, args.right_csv)
    rows_to_write = (
        [r for r in results if r["status"] != "match"] if args.only_differences else results
    )
    _write_output(args.output, rows_to_write)
    _print_summary(results)
    print(f"Output written to: {args.output}")


if __name__ == "__main__":
    main()
