# Cursor Cost Calculator

A simple Python script to calculate API costs from Cursor usage data.

## Usage

```bash
python3 cursor_cost.py <csv_file>
```

This will add an `API_COST` column to your CSV file and display total costs.

## Requirements

- Python 3
- CSV file exported from Cursor's Usage tab

## Note

Only works with usage data from August 26, 2025 and later, when Cursor started tracking token usage in the Usage tab.

To get the CSV go to Cursor dashboard -> Usage -> Click the date range in the middle of the screen and choose your start and end dates -> apply -> export CSV