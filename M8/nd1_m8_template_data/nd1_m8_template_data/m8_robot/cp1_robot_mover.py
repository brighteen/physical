#!/usr/bin/env python3
"""
CP1 — robot_mover  [스켈레톤 코드 — TODO 3개를 완성하세요]

배점: 30점
목표: /cmd_vel 발행(2Hz+) + /odom 수신 로그 + Gazebo TurtleBot4 전진

합격 기준:
    □  ros2 topic hz /cmd_vel → 2.0Hz 이상
    □  터미널에 "[INFO] 위치: x=..., y=..." 로그 출력
    □  Gazebo에서 로봇이 전진하는 것을 확인

실행 (4개 터미널):
    T1: ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=empty
    T2: ros2 run m8_robot robot_mover           (← 이 파일)
    T3: ros2 topic echo /cmd_vel
    T4: ros2 topic hz   /cmd_vel

ND1 M8 · ROS2 기초 및 로봇 시스템 통합  |  유형 B 실습중심형
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class RobotMover(Node):
    """Publisher(/cmd_vel) + Subscriber(/odom) 통합 노드."""

    def __init__(self):
        super().__init__('robot_mover')

        # ──────────────────────────────────────────────────────
        # TODO 1: /cmd_vel Publisher 생성
        #   - 메시지 타입: Twist
        #   - 토픽 이름  : '/cmd_vel'
        #   - QoS depth  : 10
        # ──────────────────────────────────────────────────────
        self.pub = None          # ← 여기를 완성하세요

        # ──────────────────────────────────────────────────────
        # TODO 2: /odom Subscriber 생성
        #   - 메시지 타입: Odometry
        #   - 토픽 이름  : '/odom'
        #   - 콜백 함수  : self._odom_cb
        #   - QoS depth  : 10
        # ──────────────────────────────────────────────────────
        self.sub = None          # ← 여기를 완성하세요

        # 0.5초마다 cmd_vel 발행 (2Hz 이상 필수)
        self.timer = self.create_timer(0.5, self._publish_cmd)

        self.get_logger().info('RobotMover 노드 시작 — TODO를 완성하세요!')

    # ── 타이머 콜백 ───────────────────────────────────────────
    def _publish_cmd(self):
        """0.5초마다 호출 → /cmd_vel 발행."""
        if self.pub is None:
            self.get_logger().warn('TODO 1 미완성 — pub이 None입니다')
            return

        # ──────────────────────────────────────────────────────
        # TODO 3: Twist 메시지를 만들어 발행하세요
        #   - msg.linear.x = 0.2  (전진 속도 0.2 m/s)
        #   - self.pub.publish(msg)
        # ──────────────────────────────────────────────────────
        msg = Twist()
        # ← 여기를 완성하세요 (linear.x 설정 + publish)

        self.get_logger().info(f'[CP1] cmd_vel 발행: v={msg.linear.x:.2f} m/s')

    # ── odom 콜백 ─────────────────────────────────────────────
    def _odom_cb(self, msg: Odometry):
        """odom 수신 시 현재 위치를 로그로 출력."""
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        self.get_logger().info(f'[CP1] 위치: x={x:.3f}, y={y:.3f}')


def main(args=None):
    rclpy.init(args=args)
    node = RobotMover()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.pub:
            node.pub.publish(Twist())   # 정지 명령
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
