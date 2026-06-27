"""실습 1 — 2DOF 해석적 IK 두 해 시각화.

산출물: results/M7_lab1_two_solutions.png
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from src.font_config import setup_korean_font
setup_korean_font()
from src.robot_arm_2dof import RobotArm2DOF
from src.ik_analytical import ik_2dof


def main():
    # 목표 4개
    targets = [(0.6, 0.0), (0.4, 0.5), (-0.2, 0.4), (0.5, -0.1)]
    robot = RobotArm2DOF()

    fig, axes = plt.subplots(1, 4, figsize=(16, 4.5))

    for ax, target in zip(axes, targets):
        sols = ik_2dof(*target)

        if sols is None:
            ax.text(0.5, 0.5, '도달 불가능', transform=ax.transAxes,
                     ha='center', va='center', fontsize=14, color='red')
            ax.set_xlim(-0.7, 0.7); ax.set_ylim(-0.7, 0.7)
            ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
            ax.set_title(f'Target {target}')
            continue

        # 두 해 시각화
        for (t1, t2), color, label in zip(
            sols, ['steelblue', 'tomato'], ['elbow up', 'elbow down']
        ):
            robot.visualize([t1, t2], ax=ax, color=color, label=label)

        # 목표 마커
        ax.plot(*target, 'X', color='red', ms=15, mew=2.5,
                 zorder=20, label='target')

        # 작업공간 원
        theta = np.linspace(0, 2 * np.pi, 100)
        ax.plot(0.6 * np.cos(theta), 0.6 * np.sin(theta),
                 '--', color='gray', alpha=0.4)

        ax.set_xlim(-0.7, 0.7); ax.set_ylim(-0.7, 0.7)
        ax.legend(fontsize=8, loc='lower right')
        ax.set_title(f'Target ({target[0]:.1f}, {target[1]:.1f})')

    plt.suptitle('실습 1 — 2DOF 해석적 IK: 두 해 (elbow up / down)',
                  fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    os.makedirs('results', exist_ok=True)
    out = 'results/M7_lab1_two_solutions2.png'
    plt.savefig(out, dpi=120, bbox_inches='tight')
    print(f'✓ 저장: {out}')


if __name__ == '__main__':
    main()
