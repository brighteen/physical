"""센서 시뮬레이터 — 카메라·라이다·IMU 가상 측정 생성.

실습 4 (칼만 필터)에서 사용. 실제 센서 없이 노이즈 추가된 측정값 생성.
"""
import numpy as np


def pinhole_camera_project(P_world, K, T_world_to_cam=None, noise_std=0.5):
    """핀홀 카메라 — 3D 세계 좌표 → 2D 픽셀.

    Parameters
    ----------
    P_world : ndarray, shape (3,)
        3D 세계 좌표 [m]
    K : ndarray, shape (3, 3)
        카메라 내부 파라미터 [[fx, 0, cx], [0, fy, cy], [0, 0, 1]]
    T_world_to_cam : ndarray, shape (4, 4), optional
        세계→카메라 동차변환. 기본 단위행렬 (카메라 = 원점)
    noise_std : float, default 0.5
        픽셀 노이즈 표준편차

    Returns
    -------
    uv : ndarray, shape (2,)
        2D 픽셀 좌표 (u, v) [pixel]
    """
    if T_world_to_cam is None:
        T_world_to_cam = np.eye(4)

    # 카메라 좌표계로 변환
    P_h = np.append(P_world, 1.0)
    P_cam = (T_world_to_cam @ P_h)[:3]

    if P_cam[2] <= 0:
        raise ValueError(f'점이 카메라 뒤에 있음 (Z={P_cam[2]:.3f})')

    # 핀홀 투영
    u = K[0, 0] * P_cam[0] / P_cam[2] + K[0, 2]
    v = K[1, 1] * P_cam[1] / P_cam[2] + K[1, 2]

    # 노이즈
    rng = np.random.default_rng()
    return np.array([u, v]) + rng.normal(0, noise_std, 2)


def lidar_distance(P_obstacle, sensor_pos=(0, 0, 0), noise_std=0.02):
    """라이다 거리 측정 — 장애물까지 거리 + 노이즈.

    Parameters
    ----------
    P_obstacle : array_like, shape (3,)
        장애물 3D 위치 [m]
    sensor_pos : array_like, shape (3,), default origin
        라이다 위치 [m]
    noise_std : float, default 0.02 [m]
        거리 측정 표준편차 (실제 라이다 ≈ ±2cm)

    Returns
    -------
    r : float
        측정 거리 [m]
    """
    P_obstacle = np.asarray(P_obstacle, dtype=float)
    sensor_pos = np.asarray(sensor_pos, dtype=float)
    true_dist = float(np.linalg.norm(P_obstacle - sensor_pos))
    rng = np.random.default_rng()
    return true_dist + float(rng.normal(0, noise_std))


def imu_accel(true_accel, bias=(0.01, 0.01, 0.01), noise_std=0.05):
    """IMU 가속도 측정 — 진짜 가속도 + 바이어스 + 노이즈.

    Parameters
    ----------
    true_accel : array_like, shape (3,)
        진짜 가속도 [m/s²]
    bias : array_like, shape (3,), default (0.01, 0.01, 0.01)
        고정 바이어스 (캘리브레이션 오류)
    noise_std : float, default 0.05 [m/s²]
        화이트 노이즈 표준편차

    Returns
    -------
    z_acc : ndarray, shape (3,)
        측정된 가속도 [m/s²]
    """
    true_accel = np.asarray(true_accel, dtype=float)
    bias = np.asarray(bias, dtype=float)
    rng = np.random.default_rng()
    return true_accel + bias + rng.normal(0, noise_std, 3)


def simulate_constant_velocity_2d(v=(1.0, 0.5), n_steps=50, dt=0.1,
                                    noise_std=0.5, seed=42):
    """2D 등속 운동 시뮬레이션 — 진짜 궤적 + 노이즈 측정.

    Parameters
    ----------
    v : tuple of float [m/s]
        등속 속도 (vx, vy)
    n_steps : int, default 50
        시뮬레이션 step 수
    dt : float, default 0.1 [s]
        시간 간격
    noise_std : float, default 0.5 [m]
        위치 측정 노이즈
    seed : int, default 42

    Returns
    -------
    truth : ndarray, shape (n, 2)
        진짜 위치 궤적
    measurements : ndarray, shape (n, 2)
        노이즈 추가된 측정 궤적
    """
    rng = np.random.default_rng(seed)
    truth = np.array([[v[0] * dt * k, v[1] * dt * k] for k in range(n_steps)])
    measurements = truth + rng.normal(0, noise_std, truth.shape)
    return truth, measurements


if __name__ == '__main__':
    print('=== sensor_simulator 검증 ===\n')

    # 1. 핀홀 카메라
    K = np.array([[500, 0, 320], [0, 500, 240], [0, 0, 1]], dtype=float)
    uv = pinhole_camera_project([0.1, 0.2, 1.0], K, noise_std=0)
    print(f'✓ 핀홀: P=(0.1,0.2,1.0) → 픽셀 (u={uv[0]:.1f}, v={uv[1]:.1f})')
    # 예상: u = 500*0.1/1.0 + 320 = 370, v = 500*0.2/1.0 + 240 = 340

    # 2. 라이다
    r = lidar_distance([3, 4, 0], noise_std=0)
    print(f'✓ 라이다: P=(3,4,0) → r={r:.3f}m (예상: 5.0)')

    # 3. IMU
    z = imu_accel([0, 0, 9.81], bias=(0, 0, 0), noise_std=0)
    print(f'✓ IMU: 진짜 (0,0,9.81) → 측정 {z}')

    # 4. 2D 등속
    truth, meas = simulate_constant_velocity_2d(v=(1.0, 0.5), n_steps=5)
    print(f'\n✓ 2D 등속 운동 (v=1.0, 0.5):')
    for i, (t, m) in enumerate(zip(truth, meas)):
        print(f'  step {i}: 진짜={t.round(2).tolist()}, 측정={m.round(2).tolist()}')
