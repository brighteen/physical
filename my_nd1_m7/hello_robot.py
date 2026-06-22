# hello_robot.py (M7 표준안 교재 4.5절)
import numpy as np
import scipy
import matplotlib
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation
import os

print('─── 환경 정보 ───')
print('NumPy :', np.__version__)
print('SciPy :', scipy.__version__)
print('Matplotlib:', matplotlib.__version__)

# 회전 행렬·쿼터니언 변환 동작 확인
r = Rotation.from_euler('ZYX', [90, 30, 45], degrees=True)
print('쿼터니언 [x,y,z,w]:', r.as_quat().round(3))
print('회전 행렬 det:', np.linalg.det(r.as_matrix()).round(6))

# 1. 그래프 그리기 전에 한글 폰트 설정 미리 적용
plt.rcParams["font.family"] = "Malgun Gothic" # Windows 맑은 고딕
plt.rcParams["axes.unicode_minus"] = False     # 마이너스 부호 깨짐 방지

# 2. matplotlib 동작 확인
fig, ax = plt.subplots(figsize=(4, 4))
theta = np.linspace(0, 2*np.pi, 100)
ax.plot(np.cos(theta), np.sin(theta))
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('환경 검증 — 단위원')

os.makedirs('results', exist_ok=True)
plt.savefig('results/env_check.png', dpi=120)
print('환경 검증 완료 — results/env_check.png 확인')
