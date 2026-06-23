"""실습 3 Step 1 — Waypoint 정의 + 연속 IK.

산출물: results/M7_lab3_waypoints.png

참고: waypoint 좌표는 M7_표준안_교재.docx 6.3.1절과 동일하게 유지됩니다.
      (작업공간 호를 따라가는 4점 경로 — 사각형이 아님)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from src.font_config import setup_korean_font
setup_korean_font()
from src.robot_arm import RobotArm3DOF
from src.ik_numerical import ik_dls


def main():
    os.makedirs('results', exist_ok=True)
    robot = RobotArm3DOF()

    # 4개 waypoint — 작업공간 호를 따라가는 경로
    waypoints = [(0.6, 0.2), (0.8, 0.0), (0.4, 0.5), (0.0, 0.8)]

    # 직전 자세를 초기값으로 사용 → 매끄러운 모션 (다중해 점프 방지)
    theta_history = []
    theta_prev = np.zeros(3)

    for wp in waypoints:
        theta, hist = ik_dls(robot, [*wp, 0], theta_init=theta_prev)
        theta_history.append(theta)
        theta_prev = theta
        print(f'WP {wp}: θ={np.degrees(theta).round(1)}°  ({len(hist)} iters)')

    # === 시각화 — 경로 + 4 자세 ===
    fig, ax = plt.subplots(figsize=(8, 8))
    for theta, wp in zip(theta_history, waypoints):
        pos, _ = robot.fk(theta)
        xs, ys, _ = zip(*pos)   # robot_arm.py fk는 (x, y, z) 3-튜플 반환
        ax.plot(xs, ys, 'o-', alpha=0.4, lw=2)

    wp_x = [w[0] for w in waypoints]
    wp_y = [w[1] for w in waypoints]
    ax.plot(wp_x, wp_y, 'r--*', ms=14, lw=2, label='Path')
    ax.plot(0, 0, 's', color='black', ms=14, label='Base')
    ax.set_xlim(-0.2, 0.9); ax.set_ylim(-0.2, 0.9)
    ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
    ax.set_title('Waypoint Path + Robot Configurations')
    ax.legend()
    plt.tight_layout()
    plt.savefig('results/M7_lab3_waypoints.png', dpi=120)
    print('저장: results/M7_lab3_waypoints.png')


if __name__ == '__main__':
    main()
