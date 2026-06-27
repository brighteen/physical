"""실습 3 Step 2 — 조작성 지형도 (Manipulability Map).

관절각 공간을 60×60 격자로 나누어 각 자세의 조작성 지수 w를 계산해
컬러맵으로 그립니다. 어두운 영역이 특이점 근방입니다.

산출물: results/M7_lab3_manipulability.png
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from src.font_config import setup_korean_font
setup_korean_font()
from src.jacobian import jacobian_analytical, manipulability  # alias → jacobian_analytical_3dof


def main():
    os.makedirs('results', exist_ok=True)

    # θ₁·θ₂ 격자 — θ₃ 고정 (시각화 용이)
    N = 60
    t1_grid = np.linspace(-np.pi, np.pi, N)
    t2_grid = np.linspace(-np.pi, np.pi, N)
    W = np.zeros((N, N))

    for i, t1 in enumerate(t1_grid):
        for j, t2 in enumerate(t2_grid):
            J = jacobian_analytical([t1, t2, 0])
            W[j, i] = manipulability(J)

    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(W, extent=[-180, 180, -180, 180],
                    origin='lower', cmap='viridis', aspect='equal')
    # plt.colorbar(im, ax=ax, label='Manipulability w = √det(JJᵀ)')
    # [수정] Matplotlib의 내장 MathText를 활용하여 전치 행렬 수식 표현
    plt.colorbar(im, ax=ax, label=r'Manipulability w = $\sqrt{\det(J J^T)}$')

    # 특이점 등고선 — 3단계 (교재 기준: 0.005=특이점, 0.05=경계, 0.15=여유)
    cs = ax.contour(np.degrees(t1_grid), np.degrees(t2_grid), W,
                    levels=[0.005, 0.05, 0.15],
                    colors=['red', 'orange', 'yellow'])
    ax.clabel(cs, inline=True, fontsize=10)

    ax.set_xlabel('θ₁ (deg)'); ax.set_ylabel('θ₂ (deg)')
    ax.set_title('Manipulability Map — θ₃ = 0°\n(Red contour = singularity zone)')
    plt.tight_layout()
    plt.savefig('results/M7_lab3_manipulability.png', dpi=120)
    print('저장: results/M7_lab3_manipulability.png')
    print(f'최대 조작성: {W.max():.4f}  (좋은 자세)')
    print(f'최소 조작성: {W.min():.4f}  (특이점)')


if __name__ == '__main__':
    main()
