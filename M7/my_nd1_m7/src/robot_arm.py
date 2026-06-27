"""3DOF 평면 로봇 팔 클래스.

L1 = 0.3, L2 = 0.3, L3 = 0.2 [m] 의 직렬 회전관절 로봇.
정기구학(FK) + 시각화 기능 제공.
"""
import numpy as np
import matplotlib.pyplot as plt
from src.robot_helpers import dh_matrix


class RobotArm3DOF:
    """3DOF 평면 로봇 팔.

    Parameters
    ----------
    L1, L2, L3 : float [m], default 0.3, 0.3, 0.2
        링크 길이

    Attributes
    ----------
    a : ndarray, shape (3,)
        DH 파라미터 a (링크 길이)
    d : ndarray, shape (3,)
        DH 파라미터 d (오프셋, 평면이므로 0)
    alpha : ndarray, shape (3,)
        DH 파라미터 α (비틀림, 평면이므로 0)

    Examples
    --------
    >>> robot = RobotArm3DOF()
    >>> positions, T = robot.fk([0.0, 0.0, 0.0])
    >>> # 모든 관절이 0일 때 말단부는 x축 0.8m 위치
    >>> np.allclose(positions[-1], [0.8, 0, 0])
    True
    """

    def __init__(self, L1=0.3, L2=0.3, L3=0.2):
        self.L1 = float(L1)
        self.L2 = float(L2)
        self.L3 = float(L3)
        self.a = np.array([L1, L2, L3], dtype=float)
        self.d = np.array([0.0, 0.0, 0.0])
        self.alpha = np.array([0.0, 0.0, 0.0])

    @property
    def link_lengths(self):
        """링크 길이 리스트 [m]."""
        return [self.L1, self.L2, self.L3]

    @property
    def reach_max(self):
        """최대 도달 거리 [m] = L1 + L2 + L3."""
        return self.L1 + self.L2 + self.L3

    @property
    def reach_min(self):
        """최소 도달 거리 [m] (작업공간 내경)."""
        # 평면 3링크의 경우 (단순화)
        return abs(self.L1 - self.L2 - self.L3) if self.L1 > self.L2 + self.L3 else 0.0

    def fk(self, thetas):
        """정기구학 — 관절각 → 말단부 위치.

        Parameters
        ----------
        thetas : array_like, shape (3,) [rad]
            세 관절각 (θ1, θ2, θ3)

        Returns
        -------
        positions : list of tuple
            [관절0, 관절1, 관절2, 말단부] 5개 위치 [m]
        T : ndarray, shape (4, 4)
            최종 동차변환행렬 (베이스 → 말단부)

        Examples
        --------
        >>> robot = RobotArm3DOF()
        >>> pos, T = robot.fk([0, 0, 0])
        >>> pos[-1][:2]    # 말단부 (x, y)
        (0.8, 0.0)
        """
        thetas = np.asarray(thetas, dtype=float)
        if thetas.shape != (3,):
            raise ValueError(f'thetas는 3개여야 합니다 (받음: {thetas.shape})')

        T = np.eye(4)
        positions = [(0.0, 0.0, 0.0)]   # 베이스 원점

        for a, d, alpha, theta in zip(self.a, self.d, self.alpha, thetas):
            T = T @ dh_matrix(a, d, alpha, theta)
            positions.append(tuple(T[:3, 3]))

        return positions, T

    def visualize(self, thetas, ax=None, color='steelblue',
                   show_workspace=False, title=None, label=None):
        """현재 자세를 matplotlib으로 시각화.

        Parameters
        ----------
        thetas : array_like, shape (3,) [rad]
        ax : matplotlib Axes, optional
        color : str, default 'steelblue'
        show_workspace : bool, default False
            작업공간 외경/내경 원 표시 여부
        title : str, optional
        label : str, optional
            범례(legend)용 라벨

        Returns
        -------
        ax : matplotlib Axes
        """
        if ax is None:
            _, ax = plt.subplots(figsize=(7, 7))

        positions, _ = self.fk(thetas)
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]

        # 링크
        ax.plot(xs, ys, '-', color=color, lw=4, solid_capstyle='round', alpha=0.85, label=label)
        # 관절
        ax.plot(xs[:-1], ys[:-1], 'o', color='#37474F', ms=12, zorder=5)
        # 베이스 (사각)
        ax.plot(0, 0, 's', color='black', ms=14)
        # 말단부 (별)
        ax.plot(xs[-1], ys[-1], '*', color='gold', ms=22,
                 markeredgecolor='red', markeredgewidth=1.5, zorder=10)

        if show_workspace:
            r_max = self.reach_max
            theta = np.linspace(0, 2 * np.pi, 100)
            ax.plot(r_max * np.cos(theta), r_max * np.sin(theta),
                     '--', color='gray', alpha=0.4, label=f'r_max={r_max:.2f}m')
            ax.legend()

        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('x [m]')
        ax.set_ylabel('y [m]')
        if title:
            ax.set_title(title)

        return ax


if __name__ == '__main__':
    print('=== RobotArm3DOF 단위 테스트 ===')

    robot = RobotArm3DOF()

    # 1. 모든 관절 0 → 일직선 펴진 자세
    pos, T = robot.fk([0, 0, 0])
    assert np.allclose(pos[-1][:2], (0.8, 0)), f'일직선 자세 실패: {pos[-1]}'
    print(f'✓ 일직선 자세: 말단부 (x, y) = ({pos[-1][0]:.3f}, {pos[-1][1]:.3f})')

    # 2. 90° 위로 접힌 자세 (θ1=90°)
    pos, _ = robot.fk([np.pi / 2, 0, 0])
    assert np.allclose(pos[-1][:2], (0, 0.8), atol=1e-6), '90° 접힌 자세 실패'
    print(f'✓ θ1=90° 자세: 말단부 (x, y) = ({pos[-1][0]:.3f}, {pos[-1][1]:.3f})')

    # 3. 작업공간
    print(f'✓ 도달 한계: r_max = {robot.reach_max:.2f} m')

    print('\n모든 테스트 통과')
