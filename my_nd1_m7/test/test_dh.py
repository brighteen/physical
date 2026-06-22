# tests/test_dh.py
import numpy as np, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.robot_helpers import dh_matrix

T0 = dh_matrix(0,0,0,0)
assert np.allclose(T0, np.eye(4)), '테스트1 실패'
print('✅ 테스트 1: 모두 0 → 단위행렬')

T1 = dh_matrix(0.3,0,0,0)
assert abs(T1[0,3]-0.3)<1e-10
print('✅ 테스트 2: a=0.3 → x이동 0.3m')

T2 = dh_matrix(0,0,0,np.pi/2)
exp = np.array([[0,-1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]])
assert np.allclose(T2, exp, atol=1e-10)
print('✅ 테스트 3: θ=90° → z축 회전')

T3 = dh_matrix(0.3,0.1,np.pi/4,np.pi/3)
assert abs(np.linalg.det(T3[:3,:3])-1.0)<1e-10
print('✅ 테스트 4: det(R) = 1.0')

R = T3[:3,:3]
assert np.allclose(R @ R.T, np.eye(3), atol=1e-10)
print('✅ 테스트 5: Rᵀ = R⁻¹')
print('\n모든 단위 테스트 통과! 4장으로 진행 가능합니다.')
