#!/usr/bin/env python3
"""
CP1 심화 — LaserScan 이상치 필터링 + RViz2 MarkerArray 시각화  [스켈레톤]

목표: 라이다 데이터에서 무효값(inf/nan/범위 초과)을 걸러내고
     유효 포인트를 RViz2에서 빨간 구(Sphere)로 시각화

합격 기준:
    □  RViz2에서 /obstacle_markers 빨간 구 표시
    □  "[INFO] [CP1 심화] 유효 포인트: N/360" 로그 정상 출력

실행:
    T1: (Gazebo + TurtleBot4 실행 중)
    T2: ros2 run m8_robot sensor_filter
    T3: ros2 run rviz2 rviz2
        → Fixed Frame: base_scan
        → Add → MarkerArray → /obstacle_markers

ND1 M8 · ROS2 기초 및 로봇 시스템 통합
"""
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Point

# ── Optional import: visualization_msgs / std_msgs ──────────────
# ROS2 환경에서만 사용 가능 — 미설치 시 HAS_VIS=False로 마커 없이 동작
try:
    from visualization_msgs.msg import Marker, MarkerArray
    from std_msgs.msg import ColorRGBA
    HAS_VIS = True
except ImportError:
    HAS_VIS = False
    Marker = MarkerArray = ColorRGBA = None


class SensorFilter(Node):
    """LaserScan 이상치 제거 → MarkerArray 발행 노드.

    visualization_msgs 미설치 환경에서도 로드 가능.
    HAS_VIS=False 시 마커 발행 없이 필터링 로그만 출력.
    """

    def __init__(self):
        super().__init__('sensor_filter')

        self.sub = self.create_subscription(
            LaserScan, '/scan', self._scan_cb, 10
        )

        if HAS_VIS:
            self.pub = self.create_publisher(MarkerArray, '/obstacle_markers', 10)
        else:
            self.pub = None
            self.get_logger().warn(
                '[CP1 심화] visualization_msgs 미설치 — 마커 발행 비활성\n'
                '  설치: sudo apt install ros-humble-visualization-msgs'
            )

        self.get_logger().info(
            f'SensorFilter 시작 — /scan 구독 대기 중  (HAS_VIS={HAS_VIS})'
        )

    def _scan_cb(self, msg: LaserScan):
        """LaserScan 수신 → 이상치 제거 → MarkerArray 발행."""
        valid_points = []

        for i, r in enumerate(msg.ranges):
            if math.isinf(r) or math.isnan(r):
                continue
            if r < msg.range_min or r > msg.range_max:
                continue
            angle = msg.angle_min + i * msg.angle_increment
            valid_points.append((i, r, angle))

        valid_count = len(valid_points)
        self.get_logger().info(
            f'[CP1 심화] 유효 포인트: {valid_count}/{len(msg.ranges)}'
        )

        if not HAS_VIS or self.pub is None:
            return

        markers = MarkerArray()
        delete_all = Marker()
        delete_all.action = Marker.DELETEALL
        markers.markers.append(delete_all)

        now_stamp = self.get_clock().now().to_msg()

        for i, r, angle in valid_points:
            x = r * math.cos(angle)
            y = r * math.sin(angle)

            m = Marker()
            m.header.frame_id = 'base_scan'
            m.header.stamp    = now_stamp
            m.id     = i
            m.type   = Marker.SPHERE
            m.action = Marker.ADD
            m.pose.position   = Point(x=x, y=y, z=0.0)
            m.pose.orientation.w = 1.0
            m.scale.x = m.scale.y = m.scale.z = 0.05
            m.color   = ColorRGBA(r=1.0, g=0.0, b=0.0, a=0.8)
            markers.markers.append(m)

        self.pub.publish(markers)


def main(args=None):
    rclpy.init(args=args)
    node = SensorFilter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
