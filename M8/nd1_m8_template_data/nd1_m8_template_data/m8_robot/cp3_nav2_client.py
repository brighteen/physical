#!/usr/bin/env python3
"""
CP3 — nav2_client  [스켈레톤 코드 — TODO 2개를 완성하세요]

배점: 40점
목표: 3개 목표 지점을 순차 자율 이동 → "도달 완료!" 로그 3줄 출력

합격 기준:
    □  "[INFO] 목표 1 도달 완료!" 로그
    □  "[INFO] 목표 2 도달 완료!" 로그
    □  "[INFO] 목표 3 도달 완료!" 로그

주의:
    ① MultiThreadedExecutor 필수 — spin() + spin_until_future_complete() 동시 사용
    ② header.stamp 설정 필수   — 없으면 TF lookup 실패
    ③ status == 4 금지         — GoalStatus.STATUS_SUCCEEDED 사용
    ④ 2D Pose Estimate 필수    — RViz2에서 초기 위치 설정 후 실행

실행 순서:
    T1: ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=maze
    T2: ros2 launch nav2_bringup bringup_launch.py \\
            map:=$HOME/map/my_map.yaml use_sim_time:=true
    T3: ros2 launch nav2_bringup rviz_launch.py
        → RViz2에서 '2D Pose Estimate' 클릭하여 초기 위치 설정 ★필수
    T4: ros2 run m8_robot cp3_nav2_client

ND1 M8 · ROS2 기초 및 로봇 시스템 통합  |  유형 B 실습중심형
"""
import math
import threading

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

# ── Optional import: rclpy.executors ────────────────────────────
# MultiThreadedExecutor가 필요하나 non-ROS2 환경(pytest)에서도 로드 가능하도록
try:
    from rclpy.executors import MultiThreadedExecutor
    HAS_EXEC = True
except ImportError:
    HAS_EXEC = False
    MultiThreadedExecutor = None

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from action_msgs.msg import GoalStatus


# ── 목표 좌표 (본인 지도 흰색 영역 좌표로 수정) ─────────────────
GOALS = [
    {'x':  1.5, 'y':  0.5, 'yaw': 0.0},   # 목표 1
    {'x':  2.5, 'y': -1.0, 'yaw': 0.0},   # 목표 2
    {'x':  0.5, 'y':  2.0, 'yaw': 0.0},   # 목표 3
]


class Nav2Client(Node):
    """NavigateToPose 액션 클라이언트 노드."""

    def __init__(self):
        super().__init__('nav2_client')

        # ──────────────────────────────────────────────────────
        # TODO 1: NavigateToPose ActionClient 생성
        #   - 액션 서버 이름: 'navigate_to_pose'
        # ──────────────────────────────────────────────────────
        self._ac = None           # ← 여기를 완성하세요
        self._executor = None     # main에서 주입

        if not HAS_EXEC:
            self.get_logger().warn(
                '[CP3] rclpy.executors 미사용 — MultiThreadedExecutor 없이 실행\n'
                '  실제 ROS2 환경에서는 정상 동작합니다.'
            )

        self.get_logger().info('Nav2Client 시작 — ActionServer 대기 중...')

    def run(self):
        """3개 목표 지점을 순서대로 이동."""
        # ──────────────────────────────────────────────────────
        # TODO 2: 아래 for 루프 안에서 send_goal()을 호출하세요
        #   - GOALS 리스트를 순서대로 순회
        #   - 각 목표에 대해 send_goal(x, y, yaw) 호출
        #   - 결과가 True이면 "도달 완료!" 로그, False이면 "실패" 로그
        # ──────────────────────────────────────────────────────
        for i, goal in enumerate(GOALS):
            pass   # ← 여기를 완성하세요

        self.get_logger().info('[CP3] ★ 모든 목표 완료!')

    def send_goal(self, x: float, y: float, yaw: float) -> bool:
        """단일 목표 지점으로 이동. 성공이면 True 반환."""
        if self._ac is None:
            self.get_logger().error('TODO 1 미완성 — _ac가 None입니다')
            return False

        if not self._ac.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('Nav2 ActionServer가 응답하지 않습니다')
            return False

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp    = self.get_clock().now().to_msg()

        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(yaw / 2.0)

        self.get_logger().info(f'  목표 전송: ({x:.2f}, {y:.2f}, yaw={yaw:.2f})')

        if self._executor is None:
            self.get_logger().error('executor 미주입 — main()에서 node._executor 설정 필요')
            return False

        send_future = self._ac.send_goal_async(
            goal_msg, feedback_callback=self._feedback_cb
        )
        self._executor.spin_until_future_complete(send_future)
        goal_handle = send_future.result()

        if not goal_handle.accepted:
            self.get_logger().warn('  목표 거부됨 — 지도 흰색 영역인지 확인하세요')
            return False

        result_future = goal_handle.get_result_async()
        self._executor.spin_until_future_complete(result_future)

        status = result_future.result().status
        return status == GoalStatus.STATUS_SUCCEEDED

    def _feedback_cb(self, feedback_msg):
        fb = feedback_msg.feedback
        dist = fb.distance_remaining
        self.get_logger().info(
            f'    남은 거리: {dist:.2f}m', throttle_duration_sec=2.0
        )


def main(args=None):
    rclpy.init(args=args)
    node = Nav2Client()

    if not HAS_EXEC:
        # non-ROS2 환경 fallback — 실제 동작 불가
        node.get_logger().error(
            'MultiThreadedExecutor 사용 불가 — 실제 ROS2 환경에서 실행하세요'
        )
        node.destroy_node()
        rclpy.shutdown()
        return

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    node._executor = executor

    t = threading.Thread(target=executor.spin, daemon=True)
    t.start()

    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
