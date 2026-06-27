#!/usr/bin/env python3
from __future__ import annotations
"""
CP2 — slam_mapper  [완성 코드 ─ TODO 없음]

배점: 30점
요구사항:
  ① SLAM Toolbox + TurtleBot4 (maze world) 로 지도 생성
  ② 키보드 텔레op으로 탐색하며 커버리지 >= 70% 달성
  ③ map_saver_cli 로 ~/map/my_map.yaml 저장
  ④ 이 노드는 지도 생성 완료 여부를 모니터링하고 결과를 로깅

실행 방법 (터미널 4개):
  T1: ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=maze
  T2: ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
  T3: ros2 launch nav2_bringup rviz_launch.py
  T4: ros2 run teleop_twist_keyboard teleop_twist_keyboard
  [충분히 탐색 후] ros2 run nav2_map_server map_saver_cli -f ~/map/my_map
  [검증] ros2 run m8_robot slam_mapper

ND1 M8 · ROS2 기초 및 로봇 시스템 통합  |  유형 B (실습중심형)
"""
import os

import rclpy
from rclpy.node import Node

# ── Optional import: rclpy.qos ───────────────────────────────────
# SLAM Toolbox /map 토픽은 TRANSIENT_LOCAL QoS 필요.
# rclpy.qos 미설치 환경(pytest, CI)에서도 모듈 로드 가능.
try:
    from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
    HAS_QOS = True
except ImportError:
    HAS_QOS = False
    QoSProfile = ReliabilityPolicy = DurabilityPolicy = None

from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import String

# ── 상수 ─────────────────────────────────────────────────────────
MAP_SAVE_DIR   = os.path.expanduser('~/map')
MAP_SAVE_FILE  = os.path.join(MAP_SAVE_DIR, 'my_map')
COVERAGE_GOAL  = 70.0
FREE_THRESHOLD   = 25
LETHAL_THRESHOLD = 65


class SlamMapper(Node):
    """
    /map 토픽을 구독하여 커버리지를 실시간 모니터링한다.

    OccupancyGrid 셀 값:
      -1        : unknown
       0 ~ 25   : free
      65 ~ 100  : occupied
    """

    def __init__(self):
        super().__init__('slam_mapper')

        # ── QoS 설정 ─────────────────────────────────────────────
        if HAS_QOS:
            map_qos = QoSProfile(
                depth=1,
                reliability=ReliabilityPolicy.RELIABLE,
                durability=DurabilityPolicy.TRANSIENT_LOCAL,
            )
        else:
            # pytest/CI 환경: 기본 QoS로 대체 (TRANSIENT_LOCAL 없음)
            map_qos = 10
            self.get_logger().warn(
                '[CP2] rclpy.qos 미사용 — 기본 QoS(depth=10) 적용\n'
                '  /map TRANSIENT_LOCAL 수신 불가 — 실제 ROS2 환경에서 재실행 권장'
            )

        # ── Subscriber / Publisher / Timer ───────────────────────
        self.sub_map = self.create_subscription(
            OccupancyGrid, '/map', self._map_cb, map_qos
        )
        self.pub_status = self.create_publisher(String, '/m8/slam_status', 10)
        self.timer      = self.create_timer(5.0, self._report_timer)

        # ── 내부 상태 ─────────────────────────────────────────────
        self._latest_map: OccupancyGrid | None = None
        self._coverage:   float = 0.0
        self._map_saved:  bool  = False

        os.makedirs(MAP_SAVE_DIR, exist_ok=True)

        self.get_logger().info(
            'SlamMapper 시작 — /map 토픽 대기 중...\n'
            f'  저장 경로   : {MAP_SAVE_FILE}.yaml / .pgm\n'
            f'  커버리지 목표: {COVERAGE_GOAL:.0f} %\n'
            f'  QoS 설정    : {"TRANSIENT_LOCAL" if HAS_QOS else "기본(depth=10)"}'
        )

    # ── /map 콜백 ─────────────────────────────────────────────────
    def _map_cb(self, msg: OccupancyGrid):
        self._latest_map = msg
        self._coverage   = self._calc_coverage(msg)

        self.get_logger().info(
            f'[CP2] 지도 수신 | '
            f'{msg.info.width}×{msg.info.height} | '
            f'{msg.info.resolution:.3f} m/cell | '
            f'커버리지={self._coverage:.1f}%'
        )

        if self._coverage >= COVERAGE_GOAL and not self._map_saved:
            self.get_logger().warn(
                f'[CP2] 커버리지 목표 달성 ({self._coverage:.1f}% >= {COVERAGE_GOAL}%)!\n'
                f'  → ros2 run nav2_map_server map_saver_cli -f {MAP_SAVE_FILE}'
            )
            self._publish_status('COVERAGE_REACHED')

    # ── 커버리지 계산 ─────────────────────────────────────────────
    @staticmethod
    def _calc_coverage(msg: OccupancyGrid) -> float:
        """free cell 비율(%) — unknown(-1) 제외."""
        data = msg.data
        if len(data) == 0:
            return 0.0
        free     = sum(1 for v in data if 0 <= v <= FREE_THRESHOLD)
        occupied = sum(1 for v in data if v >= LETHAL_THRESHOLD)
        known    = free + occupied
        return (free / known * 100.0) if known > 0 else 0.0

    # ── 주기 보고 ─────────────────────────────────────────────────
    def _report_timer(self):
        if self._latest_map is None:
            self.get_logger().warn('[CP2] /map 미수신 — SLAM Toolbox 실행 확인')
            return

        msg = self._latest_map
        area = msg.info.width * msg.info.height * msg.info.resolution ** 2
        self.get_logger().info(
            f'[CP2 보고] 커버리지={self._coverage:.1f}% / 목표={COVERAGE_GOAL}% | '
            f'면적≈{area:.1f} m²'
        )

        yaml_path = MAP_SAVE_FILE + '.yaml'
        pgm_path  = MAP_SAVE_FILE + '.pgm'
        if os.path.exists(yaml_path) and os.path.exists(pgm_path):
            if not self._map_saved:
                self._map_saved = True
                self.get_logger().info(
                    '[CP2] 지도 파일 감지! CP3으로 진행하세요.'
                )
                self._publish_status('MAP_SAVED')
        else:
            self.get_logger().info(
                f'[CP2] 지도 파일 없음 — map_saver_cli 미실행'
            )

    def _publish_status(self, status: str):
        msg = String()
        msg.data = f'CP2:{status}:coverage={self._coverage:.1f}'
        self.pub_status.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SlamMapper()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
