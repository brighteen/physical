#!/usr/bin/env python3
"""
test_coverage_calc.py — CP2 커버리지 계산 로직 단위 테스트
ROS2 없이 순수 Python으로 실행 가능

실행:
    cd nd1_m8_template
    pip install pytest
    pytest tests/ -v
"""
import pytest

# ─── OccupancyGrid 메시지 구조를 흉내 낸 stub ────────────────
class _OccupancyGridInfo:
    def __init__(self, width, height, resolution=0.05):
        self.width = width
        self.height = height
        self.resolution = resolution

class _OccupancyGrid:
    def __init__(self, data, width=10, height=10):
        self.data = data
        self.info = _OccupancyGridInfo(width, height)

# cp2_slam_mapper의 _calc_coverage 로직 추출 (rclpy 없이 테스트)
FREE_THRESHOLD   = 25
LETHAL_THRESHOLD = 65

def _calc_coverage(msg) -> float:
    """cp2_slam_mapper.SlamMapper._calc_coverage 동일 로직."""
    data  = msg.data
    total = len(data)
    if total == 0:
        return 0.0
    free     = sum(1 for v in data if 0 <= v <= FREE_THRESHOLD)
    occupied = sum(1 for v in data if v >= LETHAL_THRESHOLD)
    known    = free + occupied
    if known == 0:
        return 0.0
    return free / known * 100.0


# ─── 테스트 케이스 ──────────────────────────────────────────

class TestCoverageCalc:

    def test_all_unknown(self):
        """모든 셀 unknown(-1) → 커버리지 0%."""
        msg = _OccupancyGrid([-1] * 100)
        assert _calc_coverage(msg) == pytest.approx(0.0)

    def test_all_free(self):
        """모든 셀 free(0) → 커버리지 100%."""
        msg = _OccupancyGrid([0] * 100)
        assert _calc_coverage(msg) == pytest.approx(100.0)

    def test_all_occupied(self):
        """모든 셀 occupied(100) → free 없음 → 커버리지 0%."""
        msg = _OccupancyGrid([100] * 100)
        assert _calc_coverage(msg) == pytest.approx(0.0)

    def test_half_free_half_occupied(self):
        """free 50개 + occupied 50개 → 커버리지 50%."""
        data = [0] * 50 + [100] * 50
        msg = _OccupancyGrid(data)
        assert _calc_coverage(msg) == pytest.approx(50.0)

    def test_mixed_with_unknown(self):
        """free 70 + unknown 20 + occupied 10 → coverage=87.5%."""
        data = [0] * 70 + [-1] * 20 + [100] * 10
        msg = _OccupancyGrid(data)
        expected = 70 / (70 + 10) * 100.0
        assert _calc_coverage(msg) == pytest.approx(expected, rel=1e-6)

    def test_coverage_goal_threshold(self):
        """목표 70% 달성 여부 판단."""
        data = [0] * 70 + [100] * 30
        msg = _OccupancyGrid(data)
        assert _calc_coverage(msg) >= 70.0

    def test_empty_map(self):
        """빈 지도 → 0%."""
        msg = _OccupancyGrid([])
        assert _calc_coverage(msg) == pytest.approx(0.0)

    def test_boundary_values(self):
        """경계값: FREE_THRESHOLD=25, LETHAL_THRESHOLD=65."""
        data = [25, 26, 64, 65]   # free=1, occ=1, known=2
        msg = _OccupancyGrid(data)
        assert _calc_coverage(msg) == pytest.approx(50.0)


class TestMapSaveDetection:
    """지도 파일 저장 경로 로직 테스트."""

    def test_map_save_path_yaml(self):
        import os
        yaml_path = os.path.expanduser('~/map/my_map') + '.yaml'
        assert yaml_path.endswith('my_map.yaml')

    def test_map_save_path_pgm(self):
        import os
        pgm_path = os.path.expanduser('~/map/my_map') + '.pgm'
        assert pgm_path.endswith('my_map.pgm')
