# src/robot_helpers.py — M7 공통 헬퍼
import numpy as np

def Rz(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[ c, -s, 0],[ s, c, 0],[0, 0, 1]])
def Ry(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[ c, 0, s],[0, 1, 0],[-s, 0, c]])
def Rx(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[1, 0, 0],[0, c, -s],[0, s, c]])
def make_T(R, p):
    """3×3 회전 + 3×1 위치 → 4×4 동차변환행렬"""
    T = np.eye(4); T[:3,:3] = R; T[:3,3] = p; return T
def dh_matrix(a, d, alpha, theta):
    """DH 파라미터 → 4×4 동차변환행렬 (Standard DH)"""
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array([
    [ct, -st*ca, st*sa, a*ct],
    [st, ct*ca, -ct*sa, a*st],
    [ 0, sa, ca, d],
    [ 0, 0, 0, 1],
    ], dtype=float)
