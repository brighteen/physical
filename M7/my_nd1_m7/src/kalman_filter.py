"""칼만 필터 — 1D + 2D 위치 추정.

실습 4에서 사용. 노이즈 있는 측정값에서 진짜 상태 추정.

References
----------
- Kalman (1960). A New Approach to Linear Filtering and Prediction Problems
- Welch & Bishop (2006). An Introduction to the Kalman Filter
"""
import numpy as np


class KalmanFilter1D:
    """1D 칼만 필터 — 정지 모델 (위치 추정).

    State: x = [위치]
    Model: x_(k+1) = x_k + w,    w ~ N(0, Q)
    Meas:  z_k = x_k + v,        v ~ N(0, R)

    Parameters
    ----------
    x0 : float, default 0.0
        초기 위치 추정
    P0 : float, default 100.0
        초기 불확실성 (크게 = "초기에 모름")
    Q : float, default 0.001
        모델 노이즈 분산
    R : float, default 1.0
        측정 노이즈 분산 (센서 표준편차의 제곱)

    Examples
    --------
    >>> kf = KalmanFilter1D(x0=0.0, P0=100, Q=0.001, R=1.0)
    >>> for z in measurements:
    ...     kf.predict()
    ...     x_est, K = kf.update(z)
    """

    def __init__(self, x0=0.0, P0=100.0, Q=0.001, R=1.0):
        self.x = float(x0)
        self.P = float(P0)
        self.Q = float(Q)
        self.R = float(R)

    def predict(self):
        """예측 단계 — 정지 모델."""
        # F=1, B=0 → x_pred = x, P_pred = P + Q
        self.P = self.P + self.Q

    def update(self, z):
        """갱신 단계 — 측정값 z로 보정.

        Returns
        -------
        x_new : float
            갱신된 추정값
        K : float
            이번 step의 칼만 이득
        """
        # H=1, 직접 측정
        K = self.P / (self.P + self.R)
        self.x = self.x + K * (z - self.x)
        self.P = (1 - K) * self.P
        return self.x, K


class KalmanFilter2D:
    """2D 칼만 필터 — 등속 운동 모델 (위치 + 속도 추정).

    State: x = [x, y, vx, vy]ᵀ  (4×1)
    Model: x_(k+1) = F @ x_k + w
    Meas:  z_k = H @ x_k + v    (위치만 측정)

    Parameters
    ----------
    dt : float, default 0.1 [s]
        Time step
    Q_pos : float, default 0.01
        Position process noise variance
    Q_vel : float, default 0.1
        Velocity process noise variance
    R_meas : float, default 0.25
        Measurement noise variance (위치 측정 σ²)

    Examples
    --------
    >>> kf = KalmanFilter2D(dt=0.1, R_meas=0.25)
    >>> for z in measurements:
    ...     kf.predict()
    ...     state = kf.update(z)   # [x, y, vx, vy]
    """

    def __init__(self, dt=0.1, Q_pos=0.01, Q_vel=0.1, R_meas=0.25):
        self.dt = dt
        # State: [x, y, vx, vy]
        self.x = np.zeros(4)
        self.P = np.eye(4) * 100.0

        # State transition (constant velocity)
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1,  0],
            [0, 0, 0,  1],
        ], dtype=float)

        # Process noise
        self.Q = np.diag([Q_pos, Q_pos, Q_vel, Q_vel])

        # Measurement model (위치만)
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ], dtype=float)

        # Measurement noise
        self.R = np.eye(2) * R_meas

    def predict(self):
        """예측 단계."""
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q

    def update(self, z):
        """갱신 단계.

        Parameters
        ----------
        z : array_like, shape (2,)
            측정 위치 [x_meas, y_meas]

        Returns
        -------
        state : ndarray, shape (4,)
            추정된 상태 [x, y, vx, vy]
        """
        z = np.asarray(z, dtype=float)
        # Kalman gain
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # 갱신
        y = z - self.H @ self.x   # innovation
        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P
        return self.x.copy()


if __name__ == '__main__':
    print('=== 칼만 필터 검증 ===\n')

    # 1D 테스트
    print('▷ 1D — 정지 물체 위치 추정 (진짜=5.0)')
    rng = np.random.default_rng(42)
    kf = KalmanFilter1D(x0=0.0, P0=100.0, Q=0.001, R=1.0)
    for k in range(30):
        z = 5.0 + rng.normal(0, 1.0)
        kf.predict()
        kf.update(z)
    print(f'   최종 추정: {kf.x:.3f}m  (오차: {abs(kf.x - 5.0):.3f}m)')
    print(f'   최종 P:    {kf.P:.4f}')

    # 2D 테스트
    print('\n▷ 2D — 등속 운동 추정 (v=1.0, 0.5)')
    from src.sensor_simulator import simulate_constant_velocity_2d
    truth, meas = simulate_constant_velocity_2d(v=(1.0, 0.5), n_steps=50)

    kf2 = KalmanFilter2D(dt=0.1, R_meas=0.25)
    estimates = []
    for z in meas:
        kf2.predict()
        state = kf2.update(z)
        estimates.append(state.copy())

    estimates = np.array(estimates)
    rmse = np.sqrt(np.mean((estimates[:, :2] - truth) ** 2))
    print(f'   RMSE (위치): {rmse:.3f}m')
    print(f'   최종 속도 추정: ({estimates[-1, 2]:.3f}, {estimates[-1, 3]:.3f})  (진짜: 1.0, 0.5)')
