#!/usr/bin/env python3
"""
CP1 — robot_mover  [모범답안 — 강사용 / 배포 금지]

스켈레톤(cp1_robot_mover.py)의 TODO 3개 완성본.

검증 기준:
    ✓  ros2 topic hz /cmd_vel  →  2.0 Hz 이상
    ✓  터미널에 "[CP1] 위치: x=..., y=..." 로그 출력
    ✓  Gazebo TurtleBot4 전진 확인

실행:
    T1: ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=empty
    T2: ros2 run m8_robot robot_mover
    T3: ros2 topic hz /cmd_vel   (검증용)
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class RobotMover(Node):
    """Publisher(/cmd_vel) + Subscriber(/odom) 통합 노드."""

    def __init__(self):
        super().__init__('robot_mover')

        # ── TODO 1 완성 ── /cmd_vel Publisher 생성
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # ── TODO 2 완성 ── /odom Subscriber 생성
        self.sub = self.create_subscription(
            Odometry,
            '/odom',
            self._odom_cb,
            10,
        )

        # 0.5초(2 Hz) 타이머
        self.timer = self.create_timer(0.5, self._publish_cmd)

        self.get_logger().info('RobotMover 노드 시작!')

    # ── 타이머 콜백 ───────────────────────────────────────────
    def _publish_cmd(self):
        """0.5초마다 /cmd_vel 발행."""
        # ── TODO 3 완성 ── Twist 생성 후 발행
        msg = Twist()
        msg.linear.x = 0.2          # 전진 0.2 m/s
        msg.angular.z = 0.0         # 직진
        self.pub.publish(msg)
        self.get_logger().info(
            f'[CP1] cmd_vel 발행: linear.x={msg.linear.x:.2f} m/s'
        )

    # ── odom 콜백 ─────────────────────────────────────────────
    def _odom_cb(self, msg: Odometry):
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
        stop = Twist()              # 정지 명령
        node.pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
