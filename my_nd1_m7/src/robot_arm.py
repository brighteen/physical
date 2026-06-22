# src/robot_arm.py
import numpy as np
from robot_helpers import dh_matrix
class RobotArm3DOF:
    """평면 3DOF 직렬 로봇 — 모든 관절 z축 회전"""
    LINKS = [0.3, 0.3, 0.2] # L1, L2, L3 [m]
    def fk(self, thetas):
        T = np.eye(4)
        positions = [(0.0, 0.0)]
        for i, theta in enumerate(thetas):
            T = T @ dh_matrix(self.LINKS[i], 0, 0, theta)
            positions.append((T[0,3], T[1,3]))
        return positions, T
# 검증
from robot_arm import RobotArm3DOF

robot = RobotArm3DOF()
pos, T = robot.fk([0, 0, 0])
print('말단부:', (round(T[0,3],3), round(T[1,3],3)))
# 기대 출력: 말단부: (0.8, 0.0)