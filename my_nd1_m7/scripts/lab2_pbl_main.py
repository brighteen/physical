"""실습 2 (PBL 핵심) — 3DOF DLS 수치 IK + 수렴 분석.

산출물:
  - results/M7_lab2_convergence.png  (수렴 곡선)
  - results/M7_lab2_4poses.png       (4가지 자세)
  - results/M7_lab2_jacobian_check.png (해석 vs 수치 야코비안)
  - results/M7_lab2_summary.csv      (목표별 결과 표)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import numpy as np
import matplotlib
import matplotlib.ticker as mticker
class _AsciiMinusLogFormatter(mticker.Formatter):
    def __call__(self, x, pos=None):
        if x <= 0:
            return ''
        exp = int(round(np.log10(x)))
        # 10의 거듭제곱이 아닌 경우 대비 (예: 2*10^3 같은 경우는 필요시 확장)
        if abs(x - 10**exp) / (10**exp) > 1e-9:
            return f'{x:.1e}'.replace('e-0', 'e-').replace('e+0', 'e')
        sign = '-' if exp < 0 else ''
        return f'$10^{{{sign}{abs(exp)}}}$' if False else f'10^{sign}{abs(exp)}'
import matplotlib.pyplot as plt
from src.font_config import setup_korean_font
setup_korean_font()
from src.robot_arm import RobotArm3DOF
from src.ik_numerical import ik_dls
from src.jacobian import (jacobian_numerical, jacobian_analytical_3dof,
                          manipulability)


def main():
    robot = RobotArm3DOF()
    targets = [(0.6, 0.4), (0.4, 0.4), (0.0, 0.7), (-0.3, 0.5)]
    colors = ['steelblue', 'tomato', 'forestgreen', 'darkorange']
    os.makedirs('results', exist_ok=True)

    # ─── 1. 수렴 곡선 + 결과 표 ──────────────────────────
    fig, ax = plt.subplots(figsize=(9, 6))
    summary_rows = [['target_x', 'target_y', 'iterations', 'final_err',
                     'theta1_deg', 'theta2_deg', 'theta3_deg',
                     'manipulability_w']]

    for target, color in zip(targets, colors):
        theta, hist = ik_dls(robot, target, max_iter=10)
        
        # [수정] Matplotlib 렌더링 오류를 방지하기 위해 특수문자 ✓ 대신 (OK) 사용
        if hist[-1] < 1e-6:
            label = f'{target} ({len(hist)} iter, err={hist[-1]:.1e}) (OK)'
        else:
            label = f'{target} ({len(hist)} iter, err={hist[-1]:.1e})'

        ax.plot(hist, '-', color=color, lw=2, label=label)

        # 조작성
        J = jacobian_analytical_3dof(theta)
        w = manipulability(J)

        summary_rows.append([
            target[0], target[1], len(hist), hist[-1],
            float(np.degrees(theta[0])),
            float(np.degrees(theta[1])),
            float(np.degrees(theta[2])),
            w,
        ])

    ax.axhline(y=1e-6, color='red', linestyle='--', alpha=0.6,
                label='수렴 기준 1e-6')
    
    
    
    ax.set_yscale('log')
    ax.set_xlabel('반복 횟수 k')
    ax.set_ylabel('위치 오차 ‖e‖ [m, log scale]')

    ax.yaxis.set_major_formatter(_AsciiMinusLogFormatter())   # ← 이 줄 추가
    
    ax.set_title('IK 수렴 곡선 (DLS, λ=1e-4) — 4 목표 위치')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/M7_lab2_convergence.png', dpi=120, bbox_inches='tight')
    plt.close()
    print('✓ results/M7_lab2_convergence.png')

    # ─── 2. 4가지 자세 ──────────────────────────────────
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.5))
    for ax, target, color in zip(axes, targets, colors):
        theta, _ = ik_dls(robot, target, max_iter=0)
        robot.visualize(theta, ax=ax, color=color,
                        title=f'{target}')
        ax.plot(*target, 'X', color='red', ms=15, mew=2.5, zorder=20)
        ax.set_xlim(-0.85, 0.85); ax.set_ylim(-0.85, 0.85)
    plt.suptitle('실습 2 — 4 목표 IK 자세 결과', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('results/M7_lab2_4poses.png', dpi=120, bbox_inches='tight')
    plt.close()
    print('✓ results/M7_lab2_4poses.png')

    # ─── 3. 야코비안 검증 (해석 vs 수치) ─────────────────
    rng = np.random.default_rng(42)
    diffs = []
    for _ in range(12):
        thetas = rng.uniform(-np.pi/2, np.pi/2, 3)
        J_n = jacobian_numerical(robot, thetas)
        J_a = jacobian_analytical_3dof(thetas)
        diffs.append(np.abs(J_n - J_a).max())

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(diffs)), diffs, color='steelblue', alpha=0.85)
    ax.set_yscale('log')
    ax.axhline(y=1e-6, color='red', linestyle='--', label='허용 한계 1e-6')
    ax.set_xlabel('자세 번호 (12 random configs)')

    ax.yaxis.set_major_formatter(_AsciiMinusLogFormatter())   # ← 이 줄 추가
    
    # [수정] 유니코드 마이너스(−) 대신 키보드 기본 하이픈(-) 사용
    ax.set_ylabel('max |J_numerical - J_analytical| (log scale)')
    
    ax.set_title('야코비안 검증 — 해석 vs 수치 (max diff)')
    ax.legend(); ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('results/M7_lab2_jacobian_check.png', dpi=120, bbox_inches='tight')
    plt.close()
    print(f'✓ results/M7_lab2_jacobian_check.png (max diff = {max(diffs):.2e})')

    # ─── 4. CSV 저장 ─────────────────────────────────────
    with open('results/M7_lab2_summary.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(summary_rows)
    print('✓ results/M7_lab2_summary.csv')

    # ─── 콘솔 요약 ──────────────────────────────────────
    print('\n=== 결과 요약 ===')
    for row in summary_rows[1:]:
        tx, ty, niter, err, t1, t2, t3, w = row
        flag = '✓' if err < 1e-6 else '⚠'
        print(f'  {flag} ({tx:5.2f}, {ty:5.2f}): {niter:4d} iter, err={err:.2e}, w={w:.4f}')


if __name__ == '__main__':
    main()
