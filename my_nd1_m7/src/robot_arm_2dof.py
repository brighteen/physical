# src/robot_arm_2dof.py
"""
2DOF 평면 로봇 — 해석적 IK 학습용
"""
import numpy as np
from robot_helpers import dh_matrix

class RobotArm2DOF:
    """2DOF 평면 직렬 로봇 — 어깨 + 팔꿈치"""
    LINKS = [0.3, 0.3]  # L1, L2 [m]

    def fk(self, thetas):
        """관절각 → 말단부 위치 (x, y) + 4×4 변환행렬

        Parameters
        ----------
        thetas : (2,) array-like [θ₁, θ₂] in rad

        Returns
        -------
        positions : list of (x, y) [(0,0), 어깨끝, 말단부]
        T : (4, 4) ndarray 베이스→말단부 변환행렬
        """
        T = np.eye(4)
        positions = [(0.0, 0.0)]
        for i, theta in enumerate(thetas):
            T = T @ dh_matrix(self.LINKS[i], 0, 0, theta)
            positions.append((T[0, 3], T[1, 3]))
        return positions, T
