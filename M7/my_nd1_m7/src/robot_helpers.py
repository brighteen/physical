"""기본 회전 행렬 + DH 변환 행렬 헬퍼.

본 모듈은 Standard DH (Distal) convention을 따릅니다.
모든 각도는 라디안([rad]) 단위입니다.
"""
import numpy as np


def Rz(theta):
    """z축 회전 행렬 (3×3).

    Parameters
    ----------
    theta : float [rad]
        z축 회전 각도

    Returns
    -------
    R : ndarray, shape (3, 3)
        회전 행렬

    Examples
    --------
    >>> R = Rz(np.pi / 2)
    >>> np.allclose(R @ [1, 0, 0], [0, 1, 0])
    True
    """
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1],
    ], dtype=float)


def Ry(theta):
    """y축 회전 행렬 (3×3).

    Parameters
    ----------
    theta : float [rad]
        y축 회전 각도

    Returns
    -------
    R : ndarray, shape (3, 3)
    """
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [ c, 0, s],
        [ 0, 1, 0],
        [-s, 0, c],
    ], dtype=float)


def Rx(theta):
    """x축 회전 행렬 (3×3).

    Parameters
    ----------
    theta : float [rad]
        x축 회전 각도

    Returns
    -------
    R : ndarray, shape (3, 3)
    """
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [1, 0,  0],
        [0, c, -s],
        [0, s,  c],
    ], dtype=float)


def make_T(R, p):
    """회전(R) + 이동(p)을 4×4 동차변환행렬로 결합.

    Parameters
    ----------
    R : array_like, shape (3, 3)
        회전 행렬
    p : array_like, shape (3,)
        이동 벡터 [m]

    Returns
    -------
    T : ndarray, shape (4, 4)
        동차변환행렬

    Examples
    --------
    >>> T = make_T(np.eye(3), [1, 2, 3])
    >>> T[:3, 3].tolist()
    [1.0, 2.0, 3.0]
    """
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = np.asarray(p, dtype=float)
    return T


def dh_matrix(a, d, alpha, theta):
    """Standard DH (Distal) 4파라미터 변환 행렬.

    T_(i-1, i) = Rz(θ) · Tz(d) · Tx(a) · Rx(α)

    Parameters
    ----------
    a : float [m]
        링크 길이 (link length)
    d : float [m]
        링크 오프셋 (link offset)
    alpha : float [rad]
        링크 비틀림각 (link twist)
    theta : float [rad]
        관절 각도 (joint angle, 일반적으로 변수)

    Returns
    -------
    T : ndarray, shape (4, 4)
        i-1 좌표계에서 i 좌표계로의 동차변환행렬

    Examples
    --------
    >>> T = dh_matrix(0.3, 0, 0, 0)
    >>> np.allclose(T[:3, 3], [0.3, 0, 0])
    True
    """
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array([
        [ct, -st * ca,  st * sa, a * ct],
        [st,  ct * ca, -ct * sa, a * st],
        [0,        sa,       ca,      d],
        [0,         0,        0,      1],
    ], dtype=float)


def inv_T(T):
    """동차변환행렬의 빠른 역행렬.

    np.linalg.inv 보다 빠르고 수치 안정성 높음.

    Parameters
    ----------
    T : ndarray, shape (4, 4)

    Returns
    -------
    T_inv : ndarray, shape (4, 4)
        T 의 역행렬 (T · T_inv = I)
    """
    R = T[:3, :3]
    p = T[:3, 3]
    T_inv = np.eye(4)
    T_inv[:3, :3] = R.T
    T_inv[:3, 3] = -R.T @ p
    return T_inv


if __name__ == '__main__':
    # 단위 테스트
    print('=== robot_helpers 단위 테스트 ===')

    # 1. Rz(90°)
    R = Rz(np.pi / 2)
    assert np.allclose(R @ [1, 0, 0], [0, 1, 0]), 'Rz(90°) failed'
    assert np.allclose(np.linalg.det(R), 1.0), 'det(R) != 1'
    assert np.allclose(R.T @ R, np.eye(3)), 'R is not orthogonal'
    print('✓ Rz: 90° 회전, det=1, 정규직교')

    # 2. dh_matrix 일직선
    T = dh_matrix(0.3, 0, 0, 0)
    assert np.allclose(T[:3, 3], [0.3, 0, 0]), 'DH 단순 케이스 실패'
    print('✓ dh_matrix: 단순 평면 케이스')

    # 3. inv_T
    T = make_T(Rz(np.radians(45)), [0.5, 0.3, 0.2])
    Tinv = inv_T(T)
    assert np.allclose(T @ Tinv, np.eye(4), atol=1e-12), 'inv_T 실패'
    print('✓ inv_T: T · T_inv = I')

    print('\n모든 테스트 통과')
