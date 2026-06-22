# scripts/lab1_step3_two_solutions.py
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 현재 파일 기준 상위 디렉토리(my_nd1_m7)를 검색 경로에 추가하여 'src' 패키지를 찾을 수 있게 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.robot_arm_2dof import RobotArm2DOF
from src.ik_analytical import ik_2dof

robot = RobotArm2DOF()

# 4 가지 목표 — 각기 다른 방향의 도달 가능 지점
targets = [(0.4, 0.2), (0.3, 0.4), (-0.2, 0.4), (0.5, -0.1)]
fig, axes = plt.subplots(1, 4, figsize=(16, 4.5))

for ax, target in zip(axes, targets):
    sols = ik_2dof(*target)
    # 두 해 시각화 (elbow up / elbow down 같은 축에 겹쳐 그리기)
    for (t1, t2), color, label in zip(sols, ['steelblue', 'tomato'], ['elbow up', 'elbow down']):
        pos, _ = robot.fk([t1, t2])
        xs, ys = zip(*pos)
        ax.plot(xs, ys, 'o-', color=color, lw=3, ms=10, label=label)
        ax.plot(0, 0, 's', color='black', ms=14)
        ax.plot(*target, 'X', color='red', ms=15, mew=2.5, zorder=20, label='target')
        ax.set_xlim(-0.7, 0.7)
        ax.set_ylim(-0.7, 0.7)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc='lower right')
        ax.set_title(f'Target ({target[0]:.1f}, {target[1]:.1f})')

plt.suptitle('2DOF IK — 두 해 비교 (elbow up / down) — 4 목표', fontsize=14)
plt.tight_layout()
plt.savefig('results/M7_lab1_two_solutions.png', dpi=120)
print('저장 완료: results/M7_lab1_two_solutions.png')