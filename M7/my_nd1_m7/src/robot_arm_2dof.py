"""2DOF 평면 로봇 팔 클래스 (실습 1용).

L1 = 0.3, L2 = 0.3 [m] 의 단순 평면 로봇.
해석적 IK가 코사인 법칙으로 깔끔하게 풀리는 경우.
"""
import numpy as np
import matplotlib.pyplot as plt
from src.robot_helpers import dh_matrix


class RobotArm2DOF:
    """2DOF 평면 로봇 팔.

    Parameters
    ----------
    L1, L2 : float [m], default 0.3, 0.3

    Examples
    --------
    >>> robot = RobotArm2DOF()
    >>> pos, _ = robot.fk([np.radians(30), np.radians(60)])
    >>> # 말단부 (x, y)
    """

    def __init__(self, L1=0.3, L2=0.3):
        self.L1 = float(L1)
        self.L2 = float(L2)

    @property
    def reach_max(self):
        """최대 도달 거리 [m]."""
        return self.L1 + self.L2

    def fk(self, thetas):
        """정기구학.

        Parameters
        ----------
        thetas : array_like, shape (2,) [rad]

        Returns
        -------
        positions : list of tuple
            [관절0, 관절1, 말단부] 3개 위치
        T : ndarray, shape (4, 4)
        """
        thetas = np.asarray(thetas, dtype=float)
        if thetas.shape != (2,):
            raise ValueError(f'thetas는 2개여야 합니다 (받음: {thetas.shape})')

        T = np.eye(4)
        positions = [(0.0, 0.0, 0.0)]

        T = T @ dh_matrix(self.L1, 0, 0, thetas[0])
        positions.append(tuple(T[:3, 3]))

        T = T @ dh_matrix(self.L2, 0, 0, thetas[1])
        positions.append(tuple(T[:3, 3]))

        return positions, T

    def visualize(self, thetas, ax=None, color='steelblue', label=None):
        """matplotlib 시각화."""
        if ax is None:
            _, ax = plt.subplots(figsize=(7, 7))

        positions, _ = self.fk(thetas)
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]

        ax.plot(xs, ys, '-', color=color, lw=4, alpha=0.85, label=label)
        ax.plot(xs[:-1], ys[:-1], 'o', color='#37474F', ms=12, zorder=5)
        ax.plot(0, 0, 's', color='black', ms=14)
        ax.plot(xs[-1], ys[-1], '*', color='gold', ms=20,
                 markeredgecolor='red', markeredgewidth=1.5, zorder=10)

        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('x [m]')
        ax.set_ylabel('y [m]')
        return ax


if __name__ == '__main__':
    print('=== RobotArm2DOF 단위 테스트 ===')
    robot = RobotArm2DOF()

    # 일직선
    pos, _ = robot.fk([0, 0])
    assert np.allclose(pos[-1][:2], (0.6, 0))
    print(f'✓ 일직선: 말단부 = ({pos[-1][0]:.3f}, {pos[-1][1]:.3f})')

    # 90° 접힘
    pos, _ = robot.fk([np.pi/2, 0])
    assert np.allclose(pos[-1][:2], (0, 0.6), atol=1e-6)
    print(f'✓ 90° 접힘: 말단부 = ({pos[-1][0]:.3f}, {pos[-1][1]:.3f})')

    print('\n모든 테스트 통과')
