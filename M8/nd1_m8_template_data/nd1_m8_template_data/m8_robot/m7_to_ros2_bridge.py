#!/usr/bin/env python3
"""
m7_to_ros2_bridge.py — M7 IK 결과를 ROS2 JointState·JointTrajectory로 발행

M7 마지막 단계 ↔ M8 첫 단계 연결 브릿지.

    M7 numerical_ik() 출력 (관절각)
        → sensor_msgs/JointState     : 현재 관절 상태 발행 (RViz2 시각화)
        → trajectory_msgs/JointTrajectory : 부드러운 궤적으로 Gazebo 제어

요구 사항:
    ROS2 Humble 이상 + rclpy + sensor_msgs + trajectory_msgs

설치 (Ubuntu 22.04 + Humble):
    sudo apt install ros-humble-rclpy ros-humble-sensor-msgs
    source /opt/ros/humble/setup.bash

실행:
    ros2 run m8_robot m7_to_ros2_bridge

참고:
    ROS2 미설치 환경 → dry-run 모드 (메시지 dict 출력만)

ND1 M8 · ROS2 기초 및 로봇 시스템 통합
"""
from __future__ import annotations
import sys
import numpy as np

# ── ROS2 선택적 import ──────────────────────────────────────
try:
    import rclpy
    from rclpy.node import Node
    from rclpy.executors import SingleThreadedExecutor
    from sensor_msgs.msg import JointState
    from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
    from builtin_interfaces.msg import Duration
    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False
    print('[INFO] rclpy 미설치 — dry-run 모드 (메시지 구조만 출력)')


# ══════════════════════════════════════════════════════════════
# M7 수치 IK (교재 핵심 함수 — 직접 import 또는 인라인)
# ══════════════════════════════════════════════════════════════
def _dh_matrix(a: float, d: float, alpha: float, theta: float) -> np.ndarray:
    """Standard DH 변환 행렬 (M7 4장 핵심 함수)."""
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array([
        [ct, -st * ca,  st * sa, a * ct],
        [st,  ct * ca, -ct * sa, a * st],
        [ 0,       sa,      ca,      d],
        [ 0,        0,       0,      1],
    ])


class RobotArm3DOF:
    """M7 3DOF 평면 로봇 (l1=0.3, l2=0.3, l3=0.2 기본값)."""

    def __init__(self, links: list[float] | None = None):
        self.links = links or [0.30, 0.30, 0.20]

    def fk(self, thetas: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """FK: 관절각 → (링크별 위치 배열, 전체 T 행렬)."""
        T = np.eye(4)
        positions = [np.array([0.0, 0.0])]
        for i, theta in enumerate(thetas):
            T = T @ _dh_matrix(a=self.links[i], d=0.0, alpha=0.0, theta=theta)
            positions.append(T[:2, 3])
        return np.array(positions), T


def numerical_ik(
    robot: RobotArm3DOF,
    target: list[float],
    theta_init: list[float] | None = None,
    tol: float = 1e-6,
    max_iter: int = 1000,
    lam: float = 1e-4,
) -> tuple[np.ndarray, float, int]:
    """DLS(Damped Least Squares) 수치 IK (M7 5장 핵심 함수)."""
    n      = len(robot.links)
    theta  = np.zeros(n) if theta_init is None else np.array(theta_init, float)
    target = np.array(target, float)

    for k in range(max_iter):
        positions, _ = robot.fk(theta)
        ee = positions[-1]
        e  = target - ee
        err = float(np.linalg.norm(e))
        if err < tol:
            return theta, err, k + 1

        dq = 1e-6
        J  = np.zeros((2, n))
        for i in range(n):
            th_p = theta.copy(); th_p[i] += dq
            pos_p, _ = robot.fk(th_p)
            J[:, i] = (pos_p[-1] - ee) / dq

        JJt   = J @ J.T
        damp  = JJt + lam * lam * np.eye(2)
        theta = theta + J.T @ np.linalg.solve(damp, e)
        theta = np.arctan2(np.sin(theta), np.cos(theta))

    theta = np.arctan2(np.sin(theta), np.cos(theta))
    return theta, float(np.linalg.norm(target - robot.fk(theta)[0][-1])), max_iter


# ══════════════════════════════════════════════════════════════
# 메시지 변환 유틸리티 (ROS2 독립)
# ══════════════════════════════════════════════════════════════
def make_joint_state_dict(
    theta: np.ndarray,
    joint_names: list[str] | None = None,
    frame_id: str = 'base_link',
) -> dict:
    """관절각 배열 → JointState 메시지 dict 변환."""
    if joint_names is None:
        joint_names = [f'joint{i+1}' for i in range(len(theta))]
    return {
        'header':   {'frame_id': frame_id},
        'name':     joint_names,
        'position': theta.tolist(),
        'velocity': [0.0] * len(theta),
        'effort':   [0.0] * len(theta),
    }


def make_joint_trajectory_dict(
    waypoints: list[np.ndarray],
    joint_names: list[str] | None = None,
    time_per_wp: float = 2.0,
) -> dict:
    """관절각 웨이포인트 리스트 → JointTrajectory 메시지 dict 변환."""
    n = len(waypoints[0]) if waypoints else 3
    if joint_names is None:
        joint_names = [f'joint{i+1}' for i in range(n)]
    points = []
    for i, theta in enumerate(waypoints):
        t_sec = (i + 1) * time_per_wp
        points.append({
            'positions':  theta.tolist(),
            'velocities': [0.0] * n,
            'time_from_start': {'sec': int(t_sec), 'nanosec': 0},
        })
    return {'joint_names': joint_names, 'points': points}


# ══════════════════════════════════════════════════════════════
# ROS2 노드 (rclpy 설치 시 사용)
# ══════════════════════════════════════════════════════════════
if HAS_ROS2:
    class M7toROS2BridgeNode(Node):
        """M7 IK 결과를 ROS2 토픽으로 발행하는 브릿지 노드.

        발행 토픽:
            /joint_states                           sensor_msgs/JointState (20Hz)
            /joint_trajectory_controller/command    trajectory_msgs/JointTrajectory
        """

        JOINT_NAMES = ['joint1', 'joint2', 'joint3']

        def __init__(
            self,
            links: list[float] | None = None,
            targets: list[list[float]] | None = None,
        ):
            super().__init__('m7_to_ros2_bridge')
            self.robot   = RobotArm3DOF(links=links)
            self.targets = targets or [
                [0.55, 0.20],   # M7 PBL 목표 1
                [0.40, 0.40],   # M7 PBL 목표 2
                [0.00, 0.70],   # M7 PBL 목표 3
            ]
            self.js_pub = self.create_publisher(JointState, '/joint_states', 10)
            self.traj_pub = self.create_publisher(
                JointTrajectory, '/joint_trajectory_controller/command', 10)
            self._theta = np.zeros(3)
            self.create_timer(0.05, self._publish_joint_state)
            self.get_logger().info('M7→ROS2 브릿지 시작')
            self.get_logger().info(f'  링크 길이: {self.robot.links}')
            self.get_logger().info(f'  목표 {len(self.targets)}개 이동 예정')

        def _publish_joint_state(self):
            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name         = self.JOINT_NAMES
            msg.position     = self._theta.tolist()
            msg.velocity     = [0.0] * 3
            msg.effort       = [0.0] * 3
            self.js_pub.publish(msg)

        def run_pbl_sequence(self, time_per_wp: float = 2.5):
            """M7 PBL 3목표를 IK 계산 후 JointTrajectory로 전송."""
            solved = []
            for i, target in enumerate(self.targets):
                theta, err, iters = numerical_ik(
                    self.robot, target,
                    theta_init=self._theta.tolist(),
                    tol=1e-6, max_iter=1000, lam=1e-4,
                )
                if err > 1e-3:
                    self.get_logger().warn(f'  목표 {i+1} IK 수렴 불완전: err={err:.2e}m')
                    continue
                self._theta = theta
                solved.append(theta)
                angles_deg = [f'{np.degrees(t):.1f}°' for t in theta]
                self.get_logger().info(
                    f'  목표 {i+1} ({target}) → θ={angles_deg}  err={err:.2e}m')
            if not solved:
                self.get_logger().error('해결된 목표가 없습니다')
                return
            traj_msg = JointTrajectory()
            traj_msg.header.stamp = self.get_clock().now().to_msg()
            traj_msg.joint_names  = self.JOINT_NAMES
            for i, theta in enumerate(solved):
                pt = JointTrajectoryPoint()
                pt.positions  = theta.tolist()
                pt.velocities = [0.0] * 3
                t_total = (i + 1) * time_per_wp
                pt.time_from_start = Duration(
                    sec=int(t_total), nanosec=int((t_total % 1) * 1e9))
                traj_msg.points.append(pt)
            self.traj_pub.publish(traj_msg)
            self.get_logger().info(
                f'JointTrajectory 발행: {len(solved)}개 웨이포인트')


# ══════════════════════════════════════════════════════════════
# dry-run 유틸리티 (ROS2 미설치 환경)
# ══════════════════════════════════════════════════════════════
def dry_run_demo():
    """ROS2 없이 IK 계산 + 메시지 구조 확인."""
    print('=' * 55)
    print('M7 → ROS2 브릿지  DRY-RUN 모드')
    print('=' * 55)
    robot   = RobotArm3DOF()
    targets = [[0.55, 0.20], [0.40, 0.40], [0.00, 0.70]]
    for i, target in enumerate(targets):
        theta, err, iters = numerical_ik(robot, target)
        angles_deg = [f'{np.degrees(t):.1f}°' for t in theta]
        print(f'\n목표 {i+1}: {target}')
        print(f'  IK 해: θ = {angles_deg}  (err={err:.2e}m, {iters}회)')
        js_dict = make_joint_state_dict(theta)
        print(f'  JointState.position = {[round(p,4) for p in js_dict["position"]]}')
    print('\nJointTrajectory 웨이포인트 구조:')
    thetas = [numerical_ik(robot, t)[0] for t in targets]
    traj   = make_joint_trajectory_dict(thetas, time_per_wp=2.5)
    for j, pt in enumerate(traj['points']):
        t_sec = pt['time_from_start']['sec']
        print(f'  wp{j+1}: {[round(p,3) for p in pt["positions"]]}  t={t_sec}s')
    print('\n[OK] 메시지 구조 검증 완료 — ROS2 설치 후 실제 발행 가능')


# ══════════════════════════════════════════════════════════════
# main
# ══════════════════════════════════════════════════════════════
def main(args=None):
    if not HAS_ROS2:
        dry_run_demo()
        return

    rclpy.init(args=args)
    node = M7toROS2BridgeNode()

    import threading, time
    ex = SingleThreadedExecutor()
    ex.add_node(node)
    spin_thread = threading.Thread(target=ex.spin, daemon=True)
    spin_thread.start()

    try:
        time.sleep(3.0)
        node.run_pbl_sequence(time_per_wp=2.5)
        time.sleep(len(node.targets) * 2.5 + 2.0)
    except KeyboardInterrupt:
        pass
    finally:
        ex.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
