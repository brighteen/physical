#!/usr/bin/env python3
"""CP0 — 정사각형 경로 주행 (완성본)

파라미터:
    robot_type (str): 'turtlesim' | 'turtlebot4'  (기본: 'turtlesim')

ND1 M8 · ROS2 기초 및 로봇 시스템 통합  |  유형 B 실습중심형
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

_CONFIGS = {
    'turtlesim': {
        'topic':          '/turtle1/cmd_vel',
        'linear_speed':   1.0,
        'angular_speed':  1.0,
        'forward_ticks':  20,
        'turn_ticks':     16,
    },
    'turtlebot4': {
        'topic':          '/cmd_vel',
        'linear_speed':   0.3,
        'angular_speed':  0.5,
        'forward_ticks':  20,
        'turn_ticks':     31,   # π/2÷(0.5×0.1)=31.4→31tick≈88.8°(오차1.2°)
    },
}

class SquareMover(Node):
    TOTAL_LAPS = 3

    def __init__(self):
        super().__init__('square_mover')
        self.declare_parameter('robot_type', 'turtlesim')
        robot_type = self.get_parameter('robot_type').get_parameter_value().string_value
        if robot_type not in _CONFIGS:
            self.get_logger().warn(f"알 수 없는 robot_type='{robot_type}', 'turtlesim'으로 대체")
            robot_type = 'turtlesim'
        cfg = _CONFIGS[robot_type]
        self.LINEAR_SPEED  = cfg['linear_speed']
        self.ANGULAR_SPEED = cfg['angular_speed']
        self.FORWARD_TICKS = cfg['forward_ticks']
        self.TURN_TICKS    = cfg['turn_ticks']
        self._topic        = cfg['topic']
        self.get_logger().info(
            f'SquareMover | robot_type={robot_type} topic={self._topic} '
            f'v={self.LINEAR_SPEED}m/s w={self.ANGULAR_SPEED}rad/s'
        )
        self.pub   = self.create_publisher(Twist, self._topic, 10)
        self.timer = self.create_timer(0.1, self._on_timer)
        self._tick  = 0
        self._phase = 'FORWARD'
        self._side  = 0
        self._lap   = 0

    def _on_timer(self):
        msg = Twist()
        self._tick += 1
        if self._phase == 'FORWARD':
            msg.linear.x = self.LINEAR_SPEED
            if self._tick >= self.FORWARD_TICKS:
                self._phase = 'TURN'; self._tick = 0
        elif self._phase == 'TURN':
            msg.angular.z = self.ANGULAR_SPEED
            if self._tick >= self.TURN_TICKS:
                self._side += 1
                self.get_logger().info(f'[CP0] {self._side}변 완료')
                if self._side >= 4:
                    self._side = 0; self._lap += 1
                    self.get_logger().info(f'[CP0] ★ {self._lap}바퀴 완주!')
                    if self._lap >= self.TOTAL_LAPS:
                        self.get_logger().info(f'[CP0] ★★ {self.TOTAL_LAPS}바퀴 완주 완료 — 노드 종료')
                        self.timer.cancel(); self.pub.publish(Twist()); return
                self._phase = 'FORWARD'; self._tick = 0
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SquareMover()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally: node.pub.publish(Twist()); node.destroy_node(); rclpy.shutdown()

if __name__ == '__main__':
    main()
