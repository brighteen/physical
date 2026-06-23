"""실습 3 Step 4 — 애니메이션 GIF 생성 (선택, 가산점).

Waypoint 사이를 보간하며 로봇 팔이 경로를 따라가는 모습을 GIF로 저장합니다.

산출물: results/M7_lab3_animation.gif

요구 패키지: pillow (PillowWriter) — requirements.txt에 포함되어 있지
않다면 `pip install pillow` 필요.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from src.font_config import setup_korean_font
setup_korean_font()
from src.robot_arm import RobotArm3DOF
from src.ik_numerical import ik_dls


def main():
    os.makedirs('results', exist_ok=True)
    robot = RobotArm3DOF()

    # Step 1과 동일한 waypoint 경로 사용
    # waypoints = [(0.6, 0.2), (0.4, 0.4), (0.2, 0.5), (0.0, 0.6)]
    waypoints = [(0.6, 0.2), (0.8, 0.0), (0.4, 0.6), (0.0, 0.8)]

    # 각 waypoint 사이를 20프레임으로 보간 (마지막 → 처음 닫는 구간 포함)
    frames_per_segment = 20
    all_thetas = []
    theta_prev = np.zeros(3)

    for i in range(len(waypoints)):
        p1 = np.array(waypoints[i])
        p2 = np.array(waypoints[(i + 1) % len(waypoints)])
        for f in range(frames_per_segment):
            alpha = f / frames_per_segment
            target = (1 - alpha) * p1 + alpha * p2
            theta, _ = ik_dls(robot, [*target, 0], theta_init=theta_prev)
            all_thetas.append(theta)
            theta_prev = theta

    # 애니메이션 생성
    fig, ax = plt.subplots(figsize=(7, 7))
    line, = ax.plot([], [], 'o-', color='steelblue', lw=3, ms=10)
    tip, = ax.plot([], [], '*', color='red', ms=15)

    wp_x = [w[0] for w in waypoints] + [waypoints[0][0]]
    wp_y = [w[1] for w in waypoints] + [waypoints[0][1]]
    ax.plot(wp_x, wp_y, 'k--', alpha=0.3)
    ax.plot(0, 0, 's', color='black', ms=12)
    ax.set_xlim(-0.2, 0.9); ax.set_ylim(-0.2, 0.9)
    ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
    ax.set_title('Path Tracking — 3DOF Robot')

    def animate(frame_idx):
        theta = all_thetas[frame_idx]
        pos, _ = robot.fk(theta)
        xs, ys, _ = zip(*pos)   # robot_arm.py fk는 (x, y, z) 3-튜플 반환
        line.set_data(xs, ys)
        tip.set_data([xs[-1]], [ys[-1]])
        return line, tip

    anim = FuncAnimation(fig, animate, frames=len(all_thetas),
                          interval=50, blit=True)
    anim.save('results/M7_lab3_animation.gif',
              writer=PillowWriter(fps=20), dpi=80)
    print('저장: results/M7_lab3_animation.gif')


if __name__ == '__main__':
    main()
