#!/usr/bin/env python3
"""
analyze_map.py — 저장된 지도 파일 분석 + 커버리지 측정 스크립트
~/map/my_map.pgm 을 읽어 커버리지와 면적을 출력

실행:
    python scripts/analyze_map.py
    python scripts/analyze_map.py --map ~/map/my_map

결과 예시:
    지도 크기: 384 × 384 cells
    해상도:    0.050 m/cell
    실제 면적: 369.0 m²
    free 셀:   58,432 개
    occupied 셀: 21,184 개
    커버리지:   73.4 %  ← 목표 70% ✅

M7 참조: M7 교재 6장 OccupancyGrid 구조 설명
"""
import os
import sys
import argparse
import struct


def read_pgm(pgm_path: str):
    """PGM P5 파일 읽기 → (width, height, data) 반환."""
    with open(pgm_path, 'rb') as f:
        magic = f.readline().decode().strip()
        if magic not in ('P5', 'P2'):
            raise ValueError(f"지원하지 않는 PGM 형식: {magic}")
        # 주석 건너뛰기
        line = f.readline().decode().strip()
        while line.startswith('#'):
            line = f.readline().decode().strip()
        width, height = map(int, line.split())
        maxval = int(f.readline().decode().strip())
        raw = f.read()

    if magic == 'P5':
        data = list(raw)
    else:
        data = list(map(int, raw.split()))

    return width, height, maxval, data


def pgm_to_occupancy(data, maxval):
    """PGM 픽셀값 → OccupancyGrid 값 (0=free, 100=occupied, -1=unknown) 변환."""
    occ = []
    for v in data:
        if v >= maxval * 0.9:         # 밝음 → free
            occ.append(0)
        elif v <= maxval * 0.1:       # 어두움 → occupied
            occ.append(100)
        else:                          # 중간 → unknown
            occ.append(-1)
    return occ


def analyze(map_base: str = None):
    if map_base is None:
        map_base = os.path.expanduser('~/map/my_map')

    pgm_path  = map_base + '.pgm'
    yaml_path = map_base + '.yaml'

    # 파일 존재 확인
    if not os.path.exists(pgm_path):
        print(f"❌ 지도 파일 없음: {pgm_path}")
        print("   먼저 CP2를 완료하고 map_saver_cli로 저장하세요.")
        return

    # YAML에서 해상도 읽기
    resolution = 0.05  # 기본값
    if os.path.exists(yaml_path):
        with open(yaml_path) as f:
            for line in f:
                if 'resolution' in line:
                    resolution = float(line.split(':')[1].strip())
                    break

    # PGM 읽기
    width, height, maxval, raw_data = read_pgm(pgm_path)
    occ_data = pgm_to_occupancy(raw_data, maxval)

    # 분석
    total     = len(occ_data)
    free      = sum(1 for v in occ_data if v == 0)
    occupied  = sum(1 for v in occ_data if v == 100)
    unknown   = sum(1 for v in occ_data if v == -1)
    known     = free + occupied
    coverage  = (free / known * 100.0) if known > 0 else 0.0
    area_m2   = width * height * resolution ** 2

    print("=" * 50)
    print(" M8 CP2 — 지도 분석 결과")
    print("=" * 50)
    print(f"  파일:        {pgm_path}")
    print(f"  지도 크기:   {width} × {height} cells")
    print(f"  해상도:      {resolution:.3f} m/cell")
    print(f"  실제 면적:   {area_m2:.1f} m²")
    print(f"  free 셀:     {free:,} 개")
    print(f"  occupied 셀: {occupied:,} 개")
    print(f"  unknown 셀:  {unknown:,} 개")
    print(f"  커버리지:    {coverage:.1f} %  "
          f"{'✅ 목표 달성!' if coverage >= 70 else '⚠ 목표 미달 (70% 필요)'}")
    print("=" * 50)

    return coverage


def main():
    parser = argparse.ArgumentParser(description='M8 CP2 지도 분석')
    parser.add_argument('--map', default=None,
                        help='지도 파일 경로 (확장자 제외, 기본: ~/map/my_map)')
    args = parser.parse_args()
    analyze(args.map)


if __name__ == '__main__':
    main()
