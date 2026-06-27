#!/usr/bin/env python3
"""
test_ros2_topics.py — ROS2 토픽/메시지 타입 정합성 단위 테스트
ROS2 환경에서 실행 (ros2 run 또는 pytest 직접 실행 가능)

실행 (ROS2 환경):
    source /opt/ros/humble/setup.bash
    source ~/ros2_ws/install/setup.bash
    pytest tests/test_ros2_topics.py -v

ROS2 미설치 시 → 이 파일은 SKIP됩니다 (conftest.py 참조)
"""
import pytest

# ROS2 미설치 환경에서 자동 SKIP
rclpy = pytest.importorskip("rclpy", reason="ROS2(rclpy) 미설치 — SKIP")

from geometry_msgs.msg import Twist
from nav_msgs.msg import OccupancyGrid, Odometry
from sensor_msgs.msg import LaserScan


class TestMessageTypes:
    """M8에서 사용하는 ROS2 메시지 타입 임포트 검증."""

    def test_twist_fields(self):
        """Twist 메시지: linear.x, angular.z 필드 존재 확인."""
        msg = Twist()
        msg.linear.x  = 0.2
        msg.angular.z = 0.0
        assert msg.linear.x  == pytest.approx(0.2)
        assert msg.angular.z == pytest.approx(0.0)

    def test_odometry_pose_fields(self):
        """Odometry 메시지: pose.pose.position 필드 접근 확인."""
        msg = Odometry()
        assert hasattr(msg.pose.pose, 'position')
        assert hasattr(msg.pose.pose.position, 'x')
        assert hasattr(msg.pose.pose.position, 'y')

    def test_occupancy_grid_info(self):
        """OccupancyGrid 메시지: info.width/height/resolution 필드 확인."""
        msg = OccupancyGrid()
        msg.info.width      = 100
        msg.info.height     = 100
        msg.info.resolution = 0.05
        assert msg.info.width      == 100
        assert msg.info.height     == 100
        assert msg.info.resolution == pytest.approx(0.05)

    def test_laser_scan_ranges(self):
        """LaserScan 메시지: ranges 필드 접근 확인."""
        msg = LaserScan()
        msg.ranges = [1.0] * 360
        assert len(msg.ranges) == 360


class TestTopicNames:
    """M8 노드가 사용하는 토픽 이름 표준 확인."""

    EXPECTED_TOPICS = {
        '/cmd_vel':          'geometry_msgs/msg/Twist',
        '/odom':             'nav_msgs/msg/Odometry',
        '/scan':             'sensor_msgs/msg/LaserScan',
        '/map':              'nav_msgs/msg/OccupancyGrid',
        '/joint_states':     'sensor_msgs/msg/JointState',
        '/m8/slam_status':   'std_msgs/msg/String',
    }

    def test_topic_names_format(self):
        """토픽 이름이 '/'로 시작하는 ROS2 표준 형식인지 확인."""
        for topic in self.EXPECTED_TOPICS:
            assert topic.startswith('/'), f"토픽 '{topic}'이 '/'로 시작하지 않음"

    def test_cmd_vel_topic_name(self):
        """/cmd_vel 토픽명 표준 일치."""
        assert '/cmd_vel' in self.EXPECTED_TOPICS

    def test_map_topic_name(self):
        """/map 토픽명 표준 일치."""
        assert '/map' in self.EXPECTED_TOPICS
