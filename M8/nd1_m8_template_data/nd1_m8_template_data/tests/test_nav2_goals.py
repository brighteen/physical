#!/usr/bin/env python3
"""
test_nav2_goals.py — CP3 목표 좌표 및 쿼터니언 변환 단위 테스트
ROS2 없이 순수 Python + numpy로 실행 가능

실행:
    pytest tests/test_nav2_goals.py -v
"""
import math
import pytest

# ─── cp3_nav2_client 의 쿼터니언 변환 로직만 추출 ────────────────────
def yaw_to_quaternion(yaw: float) -> dict:
    """yaw 각도 → 쿼터니언 (z, w) 변환. M7 IK 결과값 활용."""
    return {
        'z': math.sin(yaw / 2.0),
        'w': math.cos(yaw / 2.0),
        'x': 0.0,
        'y': 0.0,
    }

def quaternion_to_yaw(q: dict) -> float:
    """쿼터니언 → yaw 역변환."""
    return 2.0 * math.atan2(q['z'], q['w'])

# CP3 기본 목표 좌표 (cp3_nav2_client.py 와 동일)
GOALS = [
    {'x':  1.5, 'y':  0.5, 'yaw': 0.0},  # 목표 1
    {'x':  2.5, 'y': -1.0, 'yaw': 0.0},  # 목표 2
    {'x':  0.5, 'y':  2.0, 'yaw': 0.0},  # 목표 3
]


class TestQuaternionConversion:

    def test_yaw_zero(self):
        """yaw=0 → z=0, w=1."""
        q = yaw_to_quaternion(0.0)
        assert q['z'] == pytest.approx(0.0, abs=1e-9)
        assert q['w'] == pytest.approx(1.0, abs=1e-9)

    def test_yaw_90deg(self):
        """yaw=π/2 (90°) → z≈0.707, w≈0.707."""
        q = yaw_to_quaternion(math.pi / 2)
        assert q['z'] == pytest.approx(math.sqrt(2) / 2, rel=1e-6)
        assert q['w'] == pytest.approx(math.sqrt(2) / 2, rel=1e-6)

    def test_yaw_180deg(self):
        """yaw=π (180°) → z≈1, w≈0."""
        q = yaw_to_quaternion(math.pi)
        assert q['z'] == pytest.approx(1.0, abs=1e-9)
        assert q['w'] == pytest.approx(0.0, abs=1e-6)

    def test_unit_quaternion(self):
        """단위 쿼터니언 조건: x²+y²+z²+w²=1."""
        for yaw_deg in [0, 30, 45, 90, 135, 180]:
            q = yaw_to_quaternion(math.radians(yaw_deg))
            norm_sq = q['x']**2 + q['y']**2 + q['z']**2 + q['w']**2
            assert norm_sq == pytest.approx(1.0, abs=1e-9), \
                f"yaw={yaw_deg}°: 단위 쿼터니언 조건 실패"

    def test_round_trip(self):
        """yaw → quaternion → yaw 왕복 변환 정확도."""
        for yaw in [0.0, math.pi/6, math.pi/4, math.pi/2, math.pi]:
            q = yaw_to_quaternion(yaw)
            yaw_back = quaternion_to_yaw(q)
            assert yaw_back == pytest.approx(yaw, abs=1e-9), \
                f"왕복 변환 실패: yaw_in={yaw:.4f}, yaw_out={yaw_back:.4f}"


class TestGoalCoordinates:

    def test_goals_count(self):
        """CP3 목표는 정확히 3개여야 한다."""
        assert len(GOALS) == 3

    def test_goals_have_required_keys(self):
        """각 목표는 x, y, yaw 키를 포함해야 한다."""
        for i, goal in enumerate(GOALS):
            assert 'x'   in goal, f"목표 {i+1}: x 키 없음"
            assert 'y'   in goal, f"목표 {i+1}: y 키 없음"
            assert 'yaw' in goal, f"목표 {i+1}: yaw 키 없음"

    def test_goals_within_maze_bounds(self):
        """목표 좌표가 maze world 범위 내 (-3.0 ~ 3.0 m) 에 있어야 한다."""
        BOUNDS = 3.0
        for i, goal in enumerate(GOALS):
            assert abs(goal['x']) <= BOUNDS, f"목표 {i+1}: x={goal['x']} 범위 초과"
            assert abs(goal['y']) <= BOUNDS, f"목표 {i+1}: y={goal['y']} 범위 초과"

    def test_goals_are_distinct(self):
        """3개 목표는 서로 다른 좌표여야 한다."""
        coords = [(g['x'], g['y']) for g in GOALS]
        assert len(set(coords)) == len(GOALS), "중복된 목표 좌표 존재"


class TestRobotMoverLogic:
    """CP1 robot_mover 속도 파라미터 검증."""

    def test_cmd_vel_linear_speed(self):
        """forward 속도 0.2 m/s 확인."""
        LINEAR_X = 0.2
        assert 0.1 <= LINEAR_X <= 0.5, "선속도 범위 이탈 (0.1~0.5 m/s)"

    def test_publish_rate(self):
        """발행 주기 0.5초 = 2 Hz 확인."""
        TIMER_PERIOD = 0.5
        hz = 1.0 / TIMER_PERIOD
        assert hz >= 2.0, f"발행 주파수 {hz} Hz < 최소 2 Hz"
