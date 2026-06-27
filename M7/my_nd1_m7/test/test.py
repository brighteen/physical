import os
import matplotlib.pyplot as plt
from src.robot_arm import RobotArm3DOF
from src.font_config import setup_korean_font
import numpy as np

setup_korean_font()

robot = RobotArm3DOF()
configs = [
    ([0, 0, 0], '기본 (0°,0°,0°)'),
    ([np.pi/2, 0, 0], '어깨 90°'),
    ([0, np.pi/2, 0], '팔꿈치 90°'),
    ([np.pi/4, np.pi/4, np.pi/4], '복합 자세'),
    ]
fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for ax, (th, lbl) in zip(axes, configs):
    robot.visualize(th, ax=ax); ax.set_title(lbl)
plt.tight_layout()

# 결과를 my_nd1_m7/results 폴더에 안전하게 저장
results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results'))
os.makedirs(results_dir, exist_ok=True)
plt.savefig(os.path.join(results_dir, 'M7_ch3_poses.png'), dpi=120)
