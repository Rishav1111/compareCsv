# CSV Font Usage Comparator

Python script to compare two CSV files by `Website_or_App_Title` for:

- `Total_Font_Use`
- `Unique_Font_Use`

The script maps records by title, compares values from both files, and generates a result CSV with match/difference status.

## Requirements

- Python 3.8+
- No external dependencies (uses Python standard library only)

## Input CSV Requirements

Both CSV files must contain these columns:

- `Website_or_App_Title`
- `Total_Font_Use`
- `Unique_Font_Use`

## Usage

From the project directory:

```bash
python3 compare_csv.py <left_csv> <right_csv>
```

Example:

```bash
python3 compare_csv.py old_data.csv new_data.csv
```

By default, this writes output to:

```text
comparison_result.csv
```

## Options

- `-o, --output <path>`: set a custom output file path
- `--only-differences`: write only rows that are different or missing in either file

Example:

```bash
python3 compare_csv.py old_data.csv new_data.csv -o diff_report.csv --only-differences
```

## Output Columns

The result CSV includes:

- `Website_or_App_Title`
- `status`
  - `match`
  - `different`
  - `missing_in_left`
  - `missing_in_right`
- For each compared field:
  - `<field>_left`
  - `<field>_right`
  - `<field>_equal`
  - `<field>_delta` (numeric difference when both values are numeric)

## Console Summary

The script prints:

- total titles compared
- number of matches
- number of differences
- number missing in left CSV
- number missing in right CSV
- output file path

## Notes

- Title mapping is case-sensitive and whitespace-trimmed.
- If duplicate titles exist in a file, the first occurrence is used.
- Numeric comparison uses decimal arithmetic when possible; otherwise raw string values are compared.
