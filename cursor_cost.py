#!/usr/bin/env python3
"""
Script to calculate API costs for Cursor usage data.
Reads a CSV file with usage events and adds an API_COST column.
No external dependencies required - uses only Python standard library.
"""

import csv
import json
import sys
from pathlib import Path

# Load pricing from JSON file
SCRIPT_DIR = Path(__file__).parent
with open(SCRIPT_DIR / 'model_pricing.json', 'r') as f:
    MODEL_PRICING = json.load(f)

def safe_float(value):
    """Convert a value to float, return 0 if empty or invalid."""
    if value == '' or value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def calculate_cost(row, headers):
    """
    Calculate the API cost for a single row based on token usage.
    """
    model_idx = headers.index('Model')
    kind_idx = headers.index('Kind')
    cache_write_idx = headers.index('Input (w/ Cache Write)')
    input_idx = headers.index('Input (w/o Cache Write)')
    cache_read_idx = headers.index('Cache Read')
    output_idx = headers.index('Output Tokens')
    
    # Skip rows that weren't charged (errors, etc.)
    kind = row[kind_idx]
    if 'No Charge' in kind or 'Errored' in kind:
        return 0.0
    
    model = row[model_idx]
    
    if model not in MODEL_PRICING:
        return 0.0
    
    pricing = MODEL_PRICING[model]
    
    cache_write_tokens = safe_float(row[cache_write_idx])
    input_tokens = safe_float(row[input_idx])
    cache_read_tokens = safe_float(row[cache_read_idx])
    output_tokens = safe_float(row[output_idx])
    
    cache_write_cost = (cache_write_tokens / 1_000_000) * pricing['cache_write']
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    cache_read_cost = (cache_read_tokens / 1_000_000) * pricing['cache_read']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    
    total_cost = cache_write_cost + input_cost + cache_read_cost + output_cost
    
    return round(total_cost, 6)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 cursor_cost.py <csv_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            rows.append(row)
    
    model_idx = headers.index('Model')
    
    costs = []
    for row in rows:
        cost = calculate_cost(row, headers)
        costs.append(cost)
    
    total_cost = sum(costs)
    
    model_costs = {}
    for row, cost in zip(rows, costs):
        model = row[model_idx]
        if model not in model_costs:
            model_costs[model] = 0.0
        model_costs[model] += cost
    
    if 'API_COST' not in headers:
        headers.append('API_COST')
        cost_idx = len(headers) - 1
    else:
        cost_idx = headers.index('API_COST')
    
    for i, row in enumerate(rows):
        while len(row) <= cost_idx:
            row.append('')
        row[cost_idx] = f"${costs[i]:.6f}"
    
    with open(input_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
    
    print(f"Total API Cost: ${total_cost:.2f}")
    print("\nCost breakdown by model:")
    for model in sorted(model_costs.keys(), key=lambda x: model_costs[x], reverse=True):
        print(f"  {model}: ${model_costs[model]:.2f}")


if __name__ == '__main__':
    main()
