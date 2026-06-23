# scripts/lab2_step1_jacobian_check.py
import numpy as np
import matplotlib.pyplot as plt
from src.robot_arm import RobotArm3DOF
from src.jacobian import jacobian_analytical, jacobian_numerical
robot = RobotArm3DOF()
# 12 가지 자세에서 두 야코비안 비교
np.random.seed(42)
configs = [np.random.uniform(-np.pi, np.pi, 3) for _ in range(12)]
errors = []
for i, th in enumerate(configs):
    J_a = jacobian_analytical(th)
    J_n = jacobian_numerical(robot, th)
    diff = np.abs(J_a - J_n).max()
    errors.append(diff)
    status = '✓' if diff < 1e-8 else '✗'
    print(f'config {i+1:2d}: max diff = {diff:.2e} {status}')

# 막대 그래프
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(range(1, 13), errors, color='steelblue')
ax.axhline(y=1e-8, color='red', linestyle='--', label='합격선 1e-8')
ax.set_yscale('log')
ax.set_xlabel('Config index')
ax.set_ylabel('Max |J_analytical − J_numerical|')
ax.set_title('Jacobian Validation (Analytical vs Numerical)')
ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/M7_lab2_jacobian_check.png', dpi=120)
print(f'\n 최대 오차: {max(errors):.2e} → {"합격" if max(errors) < 1e-8 else "불합격"}')