"""야코비안 행렬 + 조작성 지수.

수치 야코비안(중앙차분) + 해석 야코비안(3DOF 평면) + Yoshikawa 조작성.
"""
import numpy as np


def jacobian_numerical(robot, thetas, eps=1e-7):
    """중앙차분으로 수치 야코비안 계산.

    J ≈ ( f(θ+ε) − f(θ−ε) ) / (2ε)

    Parameters
    ----------
    robot : RobotArm3DOF
        fk 메소드 보유
    thetas : array_like, shape (n,) [rad]
    eps : float, default 1e-7
        섭동(perturbation) 크기

    Returns
    -------
    J : ndarray, shape (2, n)
        평면 로봇의 2×n 위치 야코비안

    Examples
    --------
    >>> from .robot_arm import RobotArm3DOF
    >>> robot = RobotArm3DOF()
    >>> J = jacobian_numerical(robot, [0.1, 0.2, 0.3])
    >>> J.shape
    (2, 3)
    """
    thetas = np.asarray(thetas, dtype=float)
    n = len(thetas)
    J = np.zeros((2, n))

    for i in range(n):
        tp = thetas.copy(); tp[i] += eps
        tm = thetas.copy(); tm[i] -= eps
        _, Tp = robot.fk(tp)
        _, Tm = robot.fk(tm)
        pp = np.array([Tp[0, 3], Tp[1, 3]])
        pm = np.array([Tm[0, 3], Tm[1, 3]])
        J[:, i] = (pp - pm) / (2 * eps)

    return J


def jacobian_analytical_3dof(thetas, L1=0.3, L2=0.3, L3=0.2):
    """3DOF 평면 로봇 해석 야코비안.

    Parameters
    ----------
    thetas : array_like, shape (3,) [rad]
    L1, L2, L3 : float [m]

    Returns
    -------
    J : ndarray, shape (2, 3)
        해석적으로 유도된 위치 야코비안
    """
    t1, t2, t3 = thetas
    # 누적각
    c1, s1 = np.cos(t1), np.sin(t1)
    c12, s12 = np.cos(t1 + t2), np.sin(t1 + t2)
    c123, s123 = np.cos(t1 + t2 + t3), np.sin(t1 + t2 + t3)

    return np.array([
        [-L1*s1 - L2*s12 - L3*s123,  -L2*s12 - L3*s123,  -L3*s123],
        [ L1*c1 + L2*c12 + L3*c123,   L2*c12 + L3*c123,   L3*c123],
    ], dtype=float)


def manipulability(J):
    """Yoshikawa 조작성 지수.

    w(θ) = √det(J · Jᵀ)

    Parameters
    ----------
    J : ndarray, shape (m, n)
        야코비안 행렬

    Returns
    -------
    w : float
        조작성 지수 (≥ 0)
        - w → 0: 특이점 근접 (역행렬 폭발 위험)
        - w 크면: 자유로운 자세

    Examples
    --------
    >>> J = np.eye(2)
    >>> manipulability(J)
    1.0
    """
    return float(np.sqrt(max(0.0, np.linalg.det(J @ J.T))))


# 교재 호환성 alias — M7_표준안_교재.docx 6장 실습 3 코드에서
# `from src.jacobian import jacobian_analytical` 형태로 import함
jacobian_analytical = jacobian_analytical_3dof


if __name__ == '__main__':
    print('=== jacobian 단위 테스트 ===')

    from .robot_arm import RobotArm3DOF
    robot = RobotArm3DOF()
    thetas = np.array([np.pi/4, np.pi/3, np.pi/6])

    # 1. 수치 vs 해석 비교
    J_n = jacobian_numerical(robot, thetas)
    J_a = jacobian_analytical_3dof(thetas)
    diff = np.abs(J_n - J_a).max()
    assert diff < 1e-6, f'수치 vs 해석 불일치: {diff:.2e}'
    print(f'✓ 수치 vs 해석 야코비안: max diff = {diff:.2e}')

    # 2. 조작성
    w = manipulability(J_a)
    assert 0 < w < 10, f'조작성 비정상: {w}'
    print(f'✓ 조작성 (현재 자세): w = {w:.4f}')

    # 3. 특이점 (완전 펴짐)
    J_sing = jacobian_analytical_3dof([0, 0, 0])
    w_sing = manipulability(J_sing)
    assert w_sing < 1e-9, f'특이점 검출 실패: {w_sing:.2e}'
    print(f'✓ 특이점 (펴짐): w = {w_sing:.2e}  (≈ 0)')

    print('\n모든 테스트 통과')
