# src/ik_analytical.py
import numpy as np
def ik_2dof(x, y, L1=0.3, L2=0.3):
    """2DOF 평면 로봇 해석적 IK

    Parameters
    ----------
    x, y : float [m] 목표 위치
    L1, L2 : float [m] 링크 길이

    Returns
    -------
    solutions : list of (θ₁, θ₂) tuple 팔꿈치 아래·위 두 해
    None 도달 불가능 (작업공간 밖)
    """
    D_sq = x**2 + y**2
    cos_t2 = (D_sq - L1**2 - L2**2) / (2 * L1 * L2)

    # 도달 가능성 — 부동소수점 안정화 후 검사
    if abs(cos_t2) > 1.0 + 1e-9:
        return None # 작업공간 밖
    cos_t2 = np.clip(cos_t2, -1.0, 1.0)
    solutions = []
    for sign in [+1, -1]: # +1=팔꿈치 아래, -1=팔꿈치 위
        t2 = sign * np.arccos(cos_t2)
        beta = np.arctan2(y, x)
        gamma = np.arctan2(L2*np.sin(t2), L1 + L2*np.cos(t2))
        t1 = beta - gamma
        solutions.append((t1, t2))
    return solutions
# === 사용 예시 + 검증 ===
if __name__ == '__main__':
    sols = ik_2dof(x=0.4, y=0.2)
    for i, (t1, t2) in enumerate(sols):
        label = '팔꿈치 아래' if i == 0 else '팔꿈치 위'
        x_fk = 0.3*np.cos(t1) + 0.3*np.cos(t1 + t2)
        y_fk = 0.3*np.sin(t1) + 0.3*np.sin(t1 + t2)
        print(f'{label}: θ=({np.degrees(t1):+6.2f}°, {np.degrees(t2):+6.2f}°)')
        print(f' FK 검증: ({x_fk:.4f}, {y_fk:.4f}) ≈ (0.4, 0.2)')
