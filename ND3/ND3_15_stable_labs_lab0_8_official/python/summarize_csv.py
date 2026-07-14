#!/usr/bin/env python3
from __future__ import annotations
import argparse
import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('csv_path')
    args = ap.parse_args()
    df = pd.read_csv(args.csv_path)
    print(df.to_string(index=False))

if __name__ == '__main__':
    main()
