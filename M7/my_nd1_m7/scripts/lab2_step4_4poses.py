# scripts/lab2_step4_4poses.py
import os
import numpy as np
import matplotlib.pyplot as plt
from src.robot_arm import RobotArm3DOF
from src.ik_numerical import ik_dls
robot = RobotArm3DOF()
targets = [(0.6, -0.6), (-0.5, 0.4), (0.3, -0.8), (-0.3, 0.5)]
fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for ax, tgt in zip(axes, targets):
    theta, hist = ik_dls(robot, [*tgt, 0])
    pos, _ = robot.fk(theta)
    xs, ys, _ = zip(*pos)
    ax.plot(xs, ys, 'o-', color='steelblue', lw=3, ms=9)
    ax.plot(0, 0, 's', color='black', ms=12)
    ax.plot(*tgt, '*', color='red', ms=18,
        markeredgecolor='gold', markeredgewidth=2)
    ax.set_xlim(-0.9, 0.9); ax.set_ylim(-0.9, 0.9)
    ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
    ax.set_title(f'{tgt} (iter={len(hist)})')
plt.suptitle('IK Solutions — 4 Targets (DLS Numerical)', fontsize=14)
plt.tight_layout()
plt.savefig('results/M7_lab2_4poses.png', dpi=120)
print('저장: results/M7_lab2_4poses.png')
