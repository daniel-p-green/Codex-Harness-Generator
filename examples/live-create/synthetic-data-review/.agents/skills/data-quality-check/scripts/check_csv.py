#!/usr/bin/env python3
import csv
import json
import sys
from collections import Counter
from pathlib import Path

path = Path(sys.argv[1])
with path.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    rows = list(reader)

columns = reader.fieldnames or []
nulls = {column: 0 for column in columns}
for row in rows:
    for column in columns:
        if row.get(column, "").strip() == "":
            nulls[column] += 1

dupes = sum(count - 1 for count in Counter(tuple(row.get(c, "") for c in columns) for row in rows).values() if count > 1)
print(json.dumps({"path": str(path), "rows": len(rows), "columns": columns, "nulls": nulls, "duplicate_rows": dupes}, indent=2))

