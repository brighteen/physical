#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    args = parser.parse_args()

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        print("Empty CSV")
        return

    # 열 너비 계산
    widths = [
        max(len(str(row[i])) for row in rows)
        for i in range(len(rows[0]))
    ]

    for row in rows:
        print(
            "  ".join(
                value.ljust(widths[i])
                for i, value in enumerate(row)
            )
        )


if __name__ == "__main__":
    main()