# conftest.py — pytest 전역 설정
#
# ROS2(rclpy) 미설치 환경에서 test_ros2_topics.py 를 자동으로 SKIP 처리합니다.
# pytest.importorskip() 이 파일 단위로 처리되므로 conftest.py 는 선택사항이지만,
# 아래 설정으로 SKIP 사유를 보다 명확하게 출력할 수 있습니다.
#
# 실행 예시 (ROS2 미설치):
#   pytest tests/ -v
#   → test_coverage_calc.py   PASSED (8개)
#   → test_nav2_goals.py      PASSED (7개)
#   → test_ros2_topics.py     SKIPPED [ROS2(rclpy) 미설치]

import pytest


def pytest_configure(config):
    """커스텀 마커 등록."""
    config.addinivalue_line(
        "markers", "ros2: ROS2 환경에서만 실행되는 테스트"
    )


def pytest_collection_modifyitems(config, items):
    """rclpy 미설치 시 ros2 마커 테스트 자동 SKIP."""
    try:
        import rclpy  # noqa: F401
    except ImportError:
        skip_ros2 = pytest.mark.skip(reason="ROS2(rclpy) 미설치 — SKIP")
        for item in items:
            if "test_ros2_topics" in str(item.fspath):
                item.add_marker(skip_ros2)
