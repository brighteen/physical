"""수치 역기구학 — 감쇠 최소자승법(DLS).

Wampler (1986) 알고리즘. 특이점 안정성을 위한 감쇠 계수 λ 사용.
"""
import numpy as np
from src.jacobian import jacobian_numerical


def ik_dls(robot, target, theta_init=None, lam=1e-4,
            tol=1e-6, max_iter=1000, alpha=0.85):
    """감쇠 최소자승법(DLS) 수치 역기구학.

    갱신식: θ_(k+1) = θ_k + α · Jᵀ ( J·Jᵀ + λ²·I )⁻¹ · e_k

    Parameters
    ----------
    robot : RobotArm3DOF
        대상 로봇 (fk 메소드 보유)
    target : array_like, shape (2,) or (3,) [m]
        목표 말단부 위치 (z는 무시, 평면 로봇)
    theta_init : array_like, shape (n,) [rad], optional
        초기 관절각. 기본 zeros
    lam : float, default 1e-4
        감쇠 계수 (특이점 안정화)
    tol : float [m], default 1e-6
        수렴 임계값 ‖e‖
    max_iter : int, default 1000
        최대 반복 횟수
    alpha : float, default 0.85
        스텝 크기 (1.0 이면 full Newton step)

    Returns
    -------
    theta : ndarray, shape (n,) [rad]
        수렴 관절각
    history : list of float
        반복별 잔차 ‖e‖ [m]

    Raises
    ------
    ValueError
        야코비안 입력 차원 불일치

    Examples
    --------
    >>> from .robot_arm import RobotArm3DOF
    >>> robot = RobotArm3DOF()
    >>> theta, hist = ik_dls(robot, [0.6, 0.2])
    >>> assert hist[-1] < 1e-6   # 수렴 확인
    """
    theta = (np.zeros(3) if theta_init is None
             else np.array(theta_init, dtype=float))
    target_xy = np.asarray(target, dtype=float)[:2]
    history = []

    for it in range(max_iter):
        # 1. 현재 FK
        _, T = robot.fk(theta)
        p_cur = np.array([T[0, 3], T[1, 3]])

        # 2. 오차
        e = target_xy - p_cur
        err = np.linalg.norm(e)
        history.append(err)

        if err < tol:
            return theta, history

        # 3. 야코비안 + DLS 의사역행렬
        J = jacobian_numerical(robot, theta)
        try:
            JJt = J @ J.T
            damped = JJt + (lam ** 2) * np.eye(JJt.shape[0])
            dtheta = J.T @ np.linalg.solve(damped, e)
        except np.linalg.LinAlgError as e:
            print(f'[Warning] Singular J at iter {it}: {e}')
            return theta, history

        # 4. 갱신
        theta = theta + alpha * dtheta

    return theta, history


def ik_dls_multi(robot, target, inits=None, **kwargs):
    """다중 초기값 IK — 지역 최솟값 회피.

    여러 초기값에서 시도 후 가장 작은 잔차의 해를 선택.

    Parameters
    ----------
    robot : RobotArm3DOF
    target : array_like
        목표 위치 [m]
    inits : list of array_like, optional
        시도할 초기값들. 기본은 다양한 자세
    **kwargs
        ik_dls 에 전달

    Returns
    -------
    best_theta : ndarray
        가장 좋은 해
    best_hist : list of float
        해당 해의 잔차 history
    """
    if inits is None:
        inits = [
            [0, 0, 0],
            [np.pi/4, np.pi/4, np.pi/4],
            [-np.pi/4, -np.pi/4, -np.pi/4],
            [np.pi/2, 0, 0],
        ]

    best_theta, best_hist, best_err = None, None, float('inf')

    for init in inits:
        theta, hist = ik_dls(robot, target, theta_init=init, **kwargs)
        err = hist[-1]
        if err < best_err:
            best_err = err
            best_theta = theta
            best_hist = hist

    return best_theta, best_hist


if __name__ == '__main__':
    print('=== ik_dls 단위 테스트 ===')

    from src.robot_arm import RobotArm3DOF
    robot = RobotArm3DOF()

    # 1. 기본 도달
    theta, hist = ik_dls(robot, [0.6, 0.2])
    assert hist[-1] < 1e-6, f'수렴 실패: {hist[-1]:.2e}'
    print(f'✓ (0.6, 0.2): {len(hist)}회 수렴, err = {hist[-1]:.2e}')

    # 2. 작업공간 경계
    theta, hist = ik_dls(robot, [0.0, 0.7], max_iter=2000)
    assert hist[-1] < 1e-3, f'경계점 수렴 실패: {hist[-1]:.2e}'
    print(f'✓ (0.0, 0.7) 경계: {len(hist)}회, err = {hist[-1]:.2e}')

    # 3. 다중 초기값
    theta, hist = ik_dls_multi(robot, [0.4, 0.4])
    print(f'✓ 다중 초기값 (0.4, 0.4): err = {hist[-1]:.2e}')

    print('\n모든 테스트 통과')
