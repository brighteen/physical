"""실습 3 Step 3 — 특이점 우회 경로 비교 (직진 vs 우회).

두 경로를 비교합니다. 직진(특이점 통과)은 야코비안 rank 부족으로
조작성이 급락하고, 우회 경로는 매끄럽게 진행됩니다.

산출물: results/M7_lab3_singularity_compare.png
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from src.font_config import setup_korean_font
setup_korean_font()
from src.robot_arm import RobotArm3DOF
from src.ik_numerical import ik_dls
from src.jacobian import jacobian_analytical, manipulability  # alias → jacobian_analytical_3dof


def follow_path(robot, path, label):
    theta_prev = np.array([0.05, 0.05, 0.0])   # 완전 일직선(특이점) 회피용 초기값
    manips = []
    for wp in path:
        theta, hist = ik_dls(robot, [*wp, 0], theta_init=theta_prev, lam=1e-3)
        w = manipulability(jacobian_analytical(theta))
        manips.append(w)
        theta_prev = theta
        print(f'  {label} WP {wp}: w={w:.4f}, iters={len(hist)}')
    return manips


def main():
    os.makedirs('results', exist_ok=True)
    robot = RobotArm3DOF()

    # 두 경로: 직진(특이점 통과) vs 우회
    # r_max = L1+L2+L3 = 0.8m 근처에서 거의 일직선 자세 통과
    path_direct = [(0.79, 0.0), (0.6, 0.0), (0.4, 0.0)]
    path_curved = [(0.79, 0.0), (0.6, 0.2), (0.4, 0.0)]

    print('=== 직진 경로 (특이점 통과) ===')
    m_direct = follow_path(robot, path_direct, 'Direct')
    print('=== 우회 경로 (특이점 회피) ===')
    m_curved = follow_path(robot, path_curved, 'Curved')

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot([0, 1, 2], m_direct, 'r-o', label='Direct (singular)', lw=2, ms=12)
    ax.plot([0, 1, 2], m_curved, 'g-o', label='Curved (avoid)', lw=2, ms=12)
    ax.axhline(y=0.01, color='black', linestyle='--', alpha=0.5,
               label='Singularity threshold')
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([f'WP {i+1}' for i in range(3)])
    ax.set_ylabel('Manipulability w')
    ax.set_title('Direct vs Curved Path Manipulability')
    ax.legend(); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/M7_lab3_singularity_compare.png', dpi=120)
    print('저장: results/M7_lab3_singularity_compare.png')


if __name__ == '__main__':
    main()
