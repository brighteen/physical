from scipy.spatial.transform import Rotation as Rsp
import numpy as np

def axis_angle_to_quat(axis, angle):
    """회전축 + 각도 → 쿼터니언 [w, x, y, z]"""
    n = np.array(axis) / np.linalg.norm(axis)
    return np.array([np.cos(angle/2), *(n * np.sin(angle/2))])
# 예: z 축 90° 회전
q = axis_angle_to_quat([0, 0, 1], np.pi/2)
print(q.round(3)) # [0.707, 0, 0, 0.707]
print('norm:', np.linalg.norm(q)) # 1.0 (단위 쿼터니언)
# scipy 로 변환 (실무 권장 — 라이브러리 검증된 코드 사용)
r = Rsp.from_euler('ZYX', [90, 30, 45], degrees=True)
print('쿼터니언 (scipy):', r.as_quat().round(3)) # ⚠ scipy: [x, y, z, w]
print('회전 행렬:\n', r.as_matrix().round(3))
print('det:', np.linalg.det(r.as_matrix()).round(6)) # 1.0
