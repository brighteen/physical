#!/usr/bin/env python3
"""
CP3 — nav2_client  [모범답안 — 강사용 / 배포 금지]

스켈레톤(cp3_nav2_client.py)의 TODO 2개 완성본.

검증 기준:
    ✓  "[INFO] 목표 1 도달 완료!" 로그
    ✓  "[INFO] 목표 2 도달 완료!" 로그
    ✓  "[INFO] 목표 3 도달 완료!" 로그

주의사항 (스켈레톤과 동일):
    ① MultiThreadedExecutor 필수
    ② header.stamp 설정 필수
    ③ GoalStatus.STATUS_SUCCEEDED 사용 (매직넘버 금지)
    ④ RViz2 '2D Pose Estimate' 설정 후 실행

실행:
    T1: ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=maze
    T2: ros2 launch nav2_bringup bringup_launch.py map:=$HOME/map/my_map.yaml use_sim_time:=true
    T3: ros2 launch nav2_bringup rviz_launch.py  (→ 2D Pose Estimate 설정 ★필수)
    T4: ros2 run m8_robot cp3_nav2_client
"""
import math
import threading

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from action_msgs.msg import GoalStatus


# ── 목표 좌표 (본인 지도 흰색 영역 좌표로 수정 가능) ──────────
GOALS = [
    {'x':  1.5, 'y':  0.5, 'yaw': 0.0},   # 목표 1
    {'x':  2.5, 'y': -1.0, 'yaw': 0.0},   # 목표 2
    {'x':  0.5, 'y':  2.0, 'yaw': 0.0},   # 목표 3
]


class Nav2Client(Node):
    """NavigateToPose 액션 클라이언트 노드."""

    def __init__(self):
        super().__init__('nav2_client')

        # ── TODO 1 완성 ── NavigateToPose ActionClient 생성
        self._ac = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.get_logger().info('Nav2Client 시작 — ActionServer 대기 중...')

    def run(self):
        """3개 목표 지점을 순서대로 이동."""
        # ── TODO 2 완성 ── GOALS 순회하며 send_goal 호출
        for i, goal in enumerate(GOALS):
            self.get_logger().info(
                f'[CP3] 목표 {i + 1} 이동 시작: '
                f"({goal['x']:.1f}, {goal['y']:.1f})"
            )
            success = self.send_goal(goal['x'], goal['y'], goal['yaw'])
            if success:
                self.get_logger().info(f'[CP3] ★ 목표 {i + 1} 도달 완료!')
            else:
                self.get_logger().error(f'[CP3] 목표 {i + 1} 실패 — 다음 목표로 진행')

        self.get_logger().info('[CP3] ★ 모든 목표 완료!')

    def send_goal(self, x: float, y: float, yaw: float) -> bool:
        """단일 목표 지점으로 이동. 성공이면 True 반환."""
        # ActionServer 준비 대기
        if not self._ac.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('Nav2 ActionServer 응답 없음')
            return False

        # ── Goal 메시지 구성 ──────────────────────────────────
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp    = self.get_clock().now().to_msg()  # ★필수

        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y

        # M7 2장 공식: w=cos(yaw/2), z=sin(yaw/2)
        goal_msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(yaw / 2.0)

        # ── 비동기 Goal 전송 ──────────────────────────────────
        self.get_logger().info(f'  목표 전송: ({x:.2f}, {y:.2f})')
        send_future = self._ac.send_goal_async(
            goal_msg,
            feedback_callback=self._feedback_cb,
        )
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()

        if not goal_handle.accepted:
            self.get_logger().warn('  목표 거부 — 지도 흰색 영역인지 확인')
            return False

        # ── 결과 대기 ─────────────────────────────────────────
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        status = result_future.result().status
        return status == GoalStatus.STATUS_SUCCEEDED   # ★매직넘버 금지

    def _feedback_cb(self, feedback_msg):
        dist = feedback_msg.feedback.distance_remaining
        self.get_logger().info(
            f'    남은 거리: {dist:.2f} m',
            throttle_duration_sec=2.0,
        )


def main(args=None):
    rclpy.init(args=args)
    node = Nav2Client()

    # ── MultiThreadedExecutor ─────────────────────────────────
    # spin()과 spin_until_future_complete()를 동시 사용하기 위해 필수
    executor = MultiThreadedExecutor()
    executor.add_node(node)

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
