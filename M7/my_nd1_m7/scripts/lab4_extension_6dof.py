"""실습 4 (확장 과제 ★★★) — UR5e 6DOF 로봇 확장.

본 교재 코드(dh_matrix, ik_dls)가 6DOF 산업 로봇에도 그대로 적용됨을 검증.

산출물:
  - results/M7_lab4_6dof_workspace.png (작업공간 단면)
  - results/M7_lab4_6dof_summary.csv  (16점 IK 결과)

학습 목표:
  ① M7에서 만든 코드의 \"일반성\" 직접 확인
  ② 산업 로봇(UR5e) DH 표를 그대로 적용
  ③ 6DOF IK는 3DOF보다 어려운 이유 체감
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import numpy as np
import matplotlib.pyplot as plt
from src.font_config import setup_korean_font
setup_korean_font()

from src.robot_helpers import dh_matrix


# ─── UR5e 6DOF DH 표 (Universal Robots 공식) ─────────────
UR5E_DH = {
    'a':     [0.0,    -0.425,   -0.3922, 0.0,     0.0,     0.0],
    'd':     [0.1625, 0.0,      0.0,     0.1333,  0.0997,  0.0996],
    'alpha': [np.pi/2, 0.0,     0.0,     np.pi/2, -np.pi/2, 0.0],
}


class RobotArm6DOF:
    """UR5e 6DOF 산업 로봇 모델."""

    def __init__(self, dh=None):
        dh = dh or UR5E_DH
        self.a = np.array(dh['a'], dtype=float)
        self.d = np.array(dh['d'], dtype=float)
        self.alpha = np.array(dh['alpha'], dtype=float)
        self.n = len(self.a)

    def fk(self, thetas):
        """6DOF FK — 행렬 곱 누적."""
        T = np.eye(4)
        positions = [(0.0, 0.0, 0.0)]
        for a, d, al, th in zip(self.a, self.d, self.alpha, thetas):
            T = T @ dh_matrix(a, d, al, th)
            positions.append(tuple(T[:3, 3]))
        return positions, T


def jacobian_6dof_position(robot, thetas, eps=1e-7):
    """6DOF 위치 야코비안 (3 × 6) — 중앙차분."""
    thetas = np.asarray(thetas, dtype=float)
    J = np.zeros((3, robot.n))
    for i in range(robot.n):
        tp = thetas.copy(); tp[i] += eps
        tm = thetas.copy(); tm[i] -= eps
        _, Tp = robot.fk(tp)
        _, Tm = robot.fk(tm)
        pp = Tp[:3, 3]
        pm = Tm[:3, 3]
        J[:, i] = (pp - pm) / (2 * eps)
    return J


def ik_dls_6dof(robot, target_xyz, theta_init=None,
                lam=1e-2, tol=1e-5, max_iter=500):
    """6DOF 수치 IK (위치만, 자세는 무시).

    Notes
    -----
    6DOF는 3DOF보다 어려움 — λ를 더 크게 (1e-2) 잡아야 안정.
    """
    theta = (np.zeros(robot.n) if theta_init is None
             else np.array(theta_init, dtype=float))
    target = np.asarray(target_xyz, dtype=float)
    history = []

    for it in range(max_iter):
        _, T = robot.fk(theta)
        p_cur = T[:3, 3]
        e = target - p_cur
        err = np.linalg.norm(e)
        history.append(err)

        if err < tol:
            return theta, history

        J = jacobian_6dof_position(robot, theta)
        try:
            JJt = J @ J.T
            damped = JJt + (lam ** 2) * np.eye(3)
            dtheta = J.T @ np.linalg.solve(damped, e)
        except np.linalg.LinAlgError:
            return theta, history

        theta = theta + 0.5 * dtheta   # 6DOF는 더 작은 step

    return theta, history


def main():
    robot = RobotArm6DOF()
    os.makedirs('results', exist_ok=True)

    print('=== 확장 과제 1 — UR5e 6DOF 확장 ===\n')

    # ─── 1. 16점 무작위 IK ───────────────────────────────
    rng = np.random.default_rng(42)
    n_targets = 16
    targets = []
    # UR5e 도달 가능한 작업공간 내 무작위 점 (반경 0.3 ~ 0.6 m)
    for _ in range(n_targets):
        r = rng.uniform(0.3, 0.6)
        phi = rng.uniform(-np.pi / 2, np.pi / 2)
        theta_sp = rng.uniform(np.pi / 6, np.pi / 2)
        x = r * np.sin(theta_sp) * np.cos(phi)
        y = r * np.sin(theta_sp) * np.sin(phi)
        z = 0.2 + r * np.cos(theta_sp)
        targets.append((x, y, z))

    # IK 풀이 + CSV 저장
    summary = [['target_x', 'target_y', 'target_z',
                 'iterations', 'final_err', 'success']]
    n_success = 0

    for target in targets:
        theta, hist = ik_dls_6dof(robot, target, max_iter=500)
        success = hist[-1] < 1e-3
        if success:
            n_success += 1
        summary.append([
            *[round(t, 4) for t in target],
            len(hist), hist[-1], success,
        ])
        flag = '✓' if success else '✗'
        print(f'  {flag} ({target[0]:5.2f}, {target[1]:5.2f}, {target[2]:5.2f}): '
               f'{len(hist):4d} iter, err={hist[-1]:.2e}')

    print(f'\n도달 성공률: {n_success}/{n_targets} = {100*n_success/n_targets:.1f}%')

    with open('results/M7_lab4_6dof_summary.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(summary)
    print('✓ results/M7_lab4_6dof_summary.csv')

    # ─── 2. 작업공간 단면 시각화 ──────────────────────────
    fig, ax = plt.subplots(figsize=(8, 7))
    success_pts = [(s[0], s[1]) for s in summary[1:] if s[5]]
    fail_pts = [(s[0], s[1]) for s in summary[1:] if not s[5]]

    if success_pts:
        xs, ys = zip(*success_pts)
        ax.scatter(xs, ys, c='steelblue', s=100, label=f'성공 ({len(success_pts)})',
                    edgecolors='navy', linewidths=1.5)
    if fail_pts:
        xs, ys = zip(*fail_pts)
        ax.scatter(xs, ys, c='red', s=100, marker='x', linewidths=2,
                    label=f'실패 ({len(fail_pts)})')

    # 작업공간 추정 원 (외경)
    theta = np.linspace(0, 2 * np.pi, 100)
    r_max = 0.85
    ax.plot(r_max * np.cos(theta), r_max * np.sin(theta),
             '--', color='gray', alpha=0.4, label=f'r_max ≈ {r_max:.2f} m')

    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_title(f'UR5e 6DOF IK — 16점 도달 검증 (Top View)\n'
                  f'성공률 {100*n_success/n_targets:.1f}% (λ=1e-2, max_iter=500)')
    ax.legend(loc='upper right')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/M7_lab4_6dof_workspace.png', dpi=120, bbox_inches='tight')
    plt.close()
    print('✓ results/M7_lab4_6dof_workspace.png')

    # ─── 3. 학습 요약 ──────────────────────────────────────
    print('\n=== 학습 요약 ===')
    print(f'  • 본 교재 dh_matrix() / DLS 알고리즘이 6DOF에 그대로 적용됨 ✓')
    print(f'  • 6DOF는 3DOF보다: λ↑ (1e-4 → 1e-2), step↓ (0.85 → 0.5)')
    print(f'  • 도달 성공률 {100*n_success/n_targets:.1f}% — 산업 솔버(TRAC-IK 99%+)와 격차')
    print(f'  → 다중 초기값 / 자세까지 포함 IK 등 개선 여지')


if __name__ == '__main__':
    main()
