"""M7 → M8 브릿지 — IK 결과를 ROS2 JointState 메시지로 발행.

본 모듈은 M7의 마지막 단계이자 M8의 첫 단계입니다.
ik_dls() 출력 → sensor_msgs/JointState → RViz2 / Gazebo / 실로봇

Requirements
------------
ROS2 Humble 이상 + rclpy + sensor_msgs

설치 (Linux Humble):
    sudo apt install ros-humble-rclpy ros-humble-sensor-msgs
    source /opt/ros/humble/setup.bash

실행:
    python3 -m src.m7_to_ros2_bridge

Notes
-----
ROS2 미설치 환경에서는 dry-run 모드로 메시지 dict 만 print.
M8 정식 학습 시작 시 본 코드를 ros2 패키지로 그대로 이관.
"""
import sys
import numpy as np

from .robot_arm import RobotArm3DOF
from .ik_numerical import ik_dls


# ─── ROS2 imports (optional) ───────────────────────────
try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import JointState
    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False
    print('[INFO] rclpy 미설치 — dry-run 모드로 실행 (메시지 구조만 출력)')


def make_joint_state_dict(theta, joint_names=None, frame_id='base_link'):
    """관절각 벡터 → JointState 메시지 dict 변환.

    ROS2 미설치 환경에서도 메시지 구조를 검증할 수 있도록 dict 반환.

    Parameters
    ----------
    theta : array_like, shape (n,) [rad]
        관절각
    joint_names : list of str, optional
        관절 이름. 기본: ['joint_1', 'joint_2', ..., 'joint_n']
    frame_id : str, default 'base_link'

    Returns
    -------
    msg_dict : dict
        JointState 호환 dict (header, name, position, velocity)

    Examples
    --------
    >>> theta = [0.5, 0.3, -0.2]
    >>> msg = make_joint_state_dict(theta)
    >>> msg['name']
    ['joint_1', 'joint_2', 'joint_3']
    >>> msg['position']
    [0.5, 0.3, -0.2]
    """
    theta = np.asarray(theta, dtype=float)
    n = len(theta)
    if joint_names is None:
        joint_names = [f'joint_{i + 1}' for i in range(n)]
    return {
        'header': {'frame_id': frame_id, 'stamp': 'now()'},
        'name': joint_names,
        'position': [float(t) for t in theta],
        'velocity': [0.0] * n,
        'effort': [0.0] * n,
    }


# ─── ROS2 노드 클래스 ──────────────────────────────────
if HAS_ROS2:

    class M7BridgeNode(Node):
        """M7 IK 결과를 sensor_msgs/JointState 로 발행하는 ROS2 노드."""

        def __init__(self, target_xy=(0.6, 0.2), publish_rate_hz=20.0):
            super().__init__('m7_bridge')
            self.publisher = self.create_publisher(
                JointState, '/joint_states', 10
            )
            self.timer = self.create_timer(
                1.0 / publish_rate_hz, self._publish_pose
            )
            self.robot = RobotArm3DOF()
            self.target = list(target_xy)
            self.get_logger().info(
                f'M7 브릿지 노드 시작 (target={target_xy}, {publish_rate_hz} Hz)'
            )

        def _publish_pose(self):
            """매 timer tick: IK 풀이 → 메시지 발행."""
            theta, hist = ik_dls(self.robot, self.target, max_iter=200)
            if hist[-1] > 1e-3:
                self.get_logger().warn(
                    f'IK 미수렴: err={hist[-1]:.2e}'
                )
                return

            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = 'base_link'
            msg.name = ['joint_1', 'joint_2', 'joint_3']
            msg.position = [float(t) for t in theta]
            msg.velocity = [0.0, 0.0, 0.0]
            self.publisher.publish(msg)


def main(args=None):
    """엔트리 포인트.

    ROS2 설치 시: 정식 노드 실행 (Ctrl+C로 종료)
    미설치 시:    dry-run 메시지 구조 출력
    """
    if HAS_ROS2:
        rclpy.init(args=args)
        node = M7BridgeNode()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()
    else:
        # Dry-run 모드 — 메시지 구조 검증
        print('=' * 60)
        print('M7 → M8 브릿지 — Dry-run 모드')
        print('=' * 60)
        robot = RobotArm3DOF()
        targets = [(0.6, 0.2), (0.4, 0.4), (0.0, 0.7)]

        for target in targets:
            theta, hist = ik_dls(robot, target, max_iter=200)
            msg = make_joint_state_dict(theta)
            print(f'\n목표 위치: {target}')
            print(f'IK 결과:  err = {hist[-1]:.2e}, iters = {len(hist)}')
            print(f'발행 메시지 (JointState):')
            for k, v in msg.items():
                if isinstance(v, list):
                    print(f'  {k}: {[round(x, 4) if isinstance(x, float) else x for x in v]}')
                else:
                    print(f'  {k}: {v}')


if __name__ == '__main__':
    main()
