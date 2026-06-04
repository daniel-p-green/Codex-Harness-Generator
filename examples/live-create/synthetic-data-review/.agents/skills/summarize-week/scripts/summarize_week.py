#!/usr/bin/env python3
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

path = Path(sys.argv[1])
date_column = sys.argv[2]
metric_column = sys.argv[3]
weekly = defaultdict(float)
with path.open(newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        week = row[date_column][:10]
        try:
            weekly[week] += float(row[metric_column])
        except ValueError:
            pass
print(json.dumps({"path": str(path), "date_column": date_column, "metric_column": metric_column, "daily_totals": dict(sorted(weekly.items()))}, indent=2))

