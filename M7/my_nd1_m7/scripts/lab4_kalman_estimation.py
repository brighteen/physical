"""실습 4 — 센서 + 칼만 필터 (1D 정지 + 2D 등속).

산출물:
  - results/M7_lab4_kalman_1d.png    (1D 정지물체 추정)
  - results/M7_lab4_kalman_2d.png    (2D 등속운동 추정)
  - results/M7_lab4_summary.csv      (Q·R 파라미터별 RMSE 비교)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import numpy as np
import matplotlib.pyplot as plt
from src.font_config import setup_korean_font
setup_korean_font()

from src.kalman_filter import KalmanFilter1D, KalmanFilter2D
from src.sensor_simulator import simulate_constant_velocity_2d


def lab4_step1_1d():
    """1D — 정지 물체 위치 추정."""
    TRUE_POS = 5.0
    n_steps = 30
    sensor_noise = 1.0
    rng = np.random.default_rng(42)

    kf = KalmanFilter1D(x0=0.0, P0=100.0, Q=0.001, R=sensor_noise ** 2)

    measurements, estimates, Ks, Ps = [], [], [], []
    for k in range(n_steps):
        z = TRUE_POS + rng.normal(0, sensor_noise)
        kf.predict()
        x_est, K = kf.update(z)
        measurements.append(z)
        estimates.append(x_est)
        Ks.append(K)
        Ps.append(kf.P)

    # 시각화 (2 subplot)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # (a) 측정 vs 추정 vs 진짜
    ax1.plot(measurements, 'o', alpha=0.5, color='gray', label='측정값 (노이즈)')
    ax1.plot(estimates, '-', lw=2.5, color='steelblue', label='칼만 추정')
    ax1.axhline(TRUE_POS, color='red', ls='--', lw=2, label=f'진짜 ({TRUE_POS}m)')
    ax1.set_xlabel('측정 #')
    ax1.set_ylabel('위치 [m]')
    ax1.set_title('1D 칼만 필터 — 정지 물체 위치 추정')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # (b) 칼만 이득 + 불확실성 수렴
    ax2_twin = ax2.twinx()
    l1 = ax2.plot(Ks, '-', color='tomato', lw=2, label='칼만 이득 K')
    l2 = ax2_twin.plot(Ps, '-', color='forestgreen', lw=2, label='불확실성 P')
    ax2.set_xlabel('측정 #')
    ax2.set_ylabel('K (칼만 이득)', color='tomato')
    ax2_twin.set_ylabel('P (불확실성)', color='forestgreen')
    ax2.set_title('칼만 이득 + 불확실성 수렴')
    ax2.legend(l1 + l2, [line.get_label() for line in l1 + l2], loc='upper right')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/M7_lab4_kalman_1d.png', dpi=120, bbox_inches='tight')
    plt.close()
    print(f'✓ results/M7_lab4_kalman_1d.png')

    # 결과 출력
    rmse = np.sqrt(np.mean((np.array(estimates) - TRUE_POS) ** 2))
    print(f'   최종 추정: {estimates[-1]:.3f}m  (진짜: {TRUE_POS}m, 오차: {abs(estimates[-1] - TRUE_POS):.3f}m)')
    print(f'   RMSE: {rmse:.4f}m, 최종 K={Ks[-1]:.4f}, 최종 P={Ps[-1]:.4f}')

    return rmse


def lab4_step2_2d():
    """2D — 등속 운동 추정."""
    truth, measurements = simulate_constant_velocity_2d(
        v=(1.0, 0.5), n_steps=50, dt=0.1, noise_std=0.5, seed=42
    )

    kf = KalmanFilter2D(dt=0.1, R_meas=0.25)
    estimates = []
    for z in measurements:
        kf.predict()
        state = kf.update(z)
        estimates.append(state.copy())
    estimates = np.array(estimates)

    # 시각화 (2 subplot)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # (a) 2D 궤적
    ax1.plot(measurements[:, 0], measurements[:, 1], 'o', alpha=0.4,
              color='gray', ms=6, label='측정 (노이즈)')
    ax1.plot(truth[:, 0], truth[:, 1], '--', lw=2, color='red', label='진짜 궤적')
    ax1.plot(estimates[:, 0], estimates[:, 1], '-', lw=2.5,
              color='steelblue', label='칼만 추정')
    ax1.set_xlabel('x [m]')
    ax1.set_ylabel('y [m]')
    ax1.set_title('2D 등속 운동 — 칼만 필터 궤적 추정')
    ax1.set_aspect('equal')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # (b) 속도 추정
    t = np.arange(len(estimates)) * 0.1
    ax2.plot(t, estimates[:, 2], '-', color='steelblue', lw=2, label='vx 추정')
    ax2.plot(t, estimates[:, 3], '-', color='forestgreen', lw=2, label='vy 추정')
    ax2.axhline(1.0, color='steelblue', ls='--', alpha=0.5, label='vx 진짜=1.0')
    ax2.axhline(0.5, color='forestgreen', ls='--', alpha=0.5, label='vy 진짜=0.5')
    ax2.set_xlabel('시간 [s]')
    ax2.set_ylabel('속도 [m/s]')
    ax2.set_title('속도 추정 수렴 (관측 안 되는 변수)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/M7_lab4_kalman_2d.png', dpi=120, bbox_inches='tight')
    plt.close()
    print(f'\n✓ results/M7_lab4_kalman_2d.png')

    # 통계
    rmse_pos = np.sqrt(np.mean((estimates[:, :2] - truth) ** 2))
    print(f'   RMSE (위치): {rmse_pos:.4f}m')
    print(f'   최종 속도 추정: vx={estimates[-1, 2]:.3f} (진짜 1.0), '
           f'vy={estimates[-1, 3]:.3f} (진짜 0.5)')

    return rmse_pos


def lab4_step3_qr_sensitivity():
    """Q·R 파라미터 변경 → 추정 정확도 분석."""
    TRUE_POS = 5.0
    sensor_noise = 1.0
    rng = np.random.default_rng(42)
    # 동일 측정값 시퀀스로 비교
    measurements = [TRUE_POS + rng.normal(0, sensor_noise) for _ in range(30)]

    configs = [
        ('정상',         0.001,  1.0),
        ('Q 너무 작음',  1e-10,  1.0),
        ('R 너무 작음',  0.001,  1e-4),
        ('Q,R 동등',     0.5,    0.5),
        ('Q 큼',         1.0,    1.0),
    ]

    rows = [['config', 'Q', 'R', 'final_estimate', 'rmse', 'final_K', 'final_P']]
    for label, Q, R in configs:
        kf = KalmanFilter1D(x0=0.0, P0=100.0, Q=Q, R=R)
        estimates = []
        for z in measurements:
            kf.predict()
            x_est, K = kf.update(z)
            estimates.append(x_est)
        rmse = np.sqrt(np.mean((np.array(estimates) - TRUE_POS) ** 2))
        rows.append([label, Q, R, estimates[-1], rmse, K, kf.P])

    with open('results/M7_lab4_summary.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f'\n✓ results/M7_lab4_summary.csv')

    print('\n=== Q·R 민감도 분석 ===')
    print(f'{"Config":18s} {"Q":>10s} {"R":>10s} {"Final":>8s} {"RMSE":>8s}')
    for row in rows[1:]:
        print(f'{row[0]:18s} {row[1]:>10.4g} {row[2]:>10.4g} '
               f'{row[3]:>8.3f} {row[4]:>8.4f}')


def main():
    print('=== 실습 4 — 센서 + 칼만 필터 ===\n')
    print('▶ Step 1 — 1D 정지 물체 위치 추정')
    rmse_1d = lab4_step1_1d()

    print('\n▶ Step 2 — 2D 등속 운동 추정')
    rmse_2d = lab4_step2_2d()

    print('\n▶ Step 3 — Q·R 파라미터 민감도 분석')
    lab4_step3_qr_sensitivity()

    print('\n=== 실습 4 완료 ===')
    if rmse_1d < 0.3:
        print(f'✓ 1D RMSE = {rmse_1d:.4f}m < 0.3 (합격)')
    if rmse_2d < 0.5:
        print(f'✓ 2D RMSE = {rmse_2d:.4f}m < 0.5 (합격)')


if __name__ == '__main__':
    main()
