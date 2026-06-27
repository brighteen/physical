# 오도메트리 누적 계산 예시
import numpy as np

class DiffDriveOdom:
    def __init__(self, wheel_radius=0.033, wheel_base=0.160):
        self.r = wheel_radius  # TurtleBot3 기본값 (m)
        self.L = wheel_base    # TurtleBot3 기본값 (m)
        self.x, self.y, self.th = 0.0, 0.0, 0.0

    def update(self, omega_R, omega_L, dt):
        """omega_R, omega_L: 바퀴 각속도(rad/s), dt: 경과 시간(s)"""
        v = self.r * (omega_R + omega_L) / 2.0
        w = self.r * (omega_R - omega_L) / self.L
        self.x += v * np.cos(self.th) * dt
        self.y += v * np.sin(self.th) * dt
        self.th += w * dt
        return self.x, self.y, self.th

# 사용 예: 0.5 m/s 직진 1 초
odom = DiffDriveOdom()
# omega = v / r → 0.5 / 0.033 ≈ 15.15 rad/s
omega = 0.5 / 0.033
x, y, th = odom.update(omega, omega, 1.0)
print(f'위치: ({x:.3f}, {y:.3f}), 방위: {np.degrees(th):.1f}°')
# 출력 예: 위치: (0.500, 0.000), 방위: 0.0°
