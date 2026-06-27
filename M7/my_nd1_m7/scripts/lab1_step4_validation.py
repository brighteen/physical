import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from src.font_config import setup_korean_font
setup_korean_font()
from src.robot_arm_2dof import RobotArm2DOF
from src.ik_analytical import ik_2dof

def main():
    robot = RobotArm2DOF()

    # 4×4 격자
    xs = np.linspace(-0.5, 0.5, 4)
    ys = np.linspace(-0.5, 0.5, 4)

    fig, ax = plt.subplots(figsize=(8, 8))
    reachable_count = 0

    for x in xs:
        for y in ys:
            sols = ik_2dof(x, y)
            if sols is None:
                ax.plot(x, y, 'x', color='red', ms=12, mew=3)
            else:
                ax.plot(x, y, 'o', color='green', ms=10)
                
                # 검증: 첫 번째 해로 FK
                pos, _ = robot.fk(sols[1])
                
                # [수정된 부분] 3D 좌표(x, y, z)가 반환되므로 Z축은 언더스코어(_)로 무시
                xs_arm, ys_arm, _ = zip(*pos)
                
                ax.plot(xs_arm, ys_arm, '-', color='lightblue', alpha=0.4)
                reachable_count += 1

    # 작업공간 도넛 (외경 0.6, 내경 0)
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(0.6*np.cos(theta), 0.6*np.sin(theta), '--', color='purple', label='외경 r=L1+L2')
    ax.plot(0, 0, 's', color='black', ms=14, label='베이스')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title(f'Reachability — {reachable_count}/16 reachable')
    ax.legend()
    
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/M7_lab1_validation_elbow_down.png', dpi=120)
    print(f'도달 가능: {reachable_count}/16 — 작업공간 외 점은 빨간 X 표시')

if __name__ == '__main__':
    main()