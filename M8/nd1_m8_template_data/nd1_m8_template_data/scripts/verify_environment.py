#!/usr/bin/env python3
"""
verify_environment.py — M8 실습 환경 사전 검증 스크립트
ROS2 설치 여부 + 필수 패키지 확인

실행:
    python scripts/verify_environment.py

출력 예시:
    [1/6] Python 버전 ... 3.10.12 ✅
    [2/6] ROS2 환경 ... humble ✅
    ...
    ✅ 6/6 모두 통과 — 실습 준비 완료!
"""
import sys
import os
import subprocess


def check_python():
    v = sys.version_info
    ver = f"{v.major}.{v.minor}.{v.micro}"
    if v >= (3, 10):
        return True, ver
    return False, f"{ver} (3.10+ 권장)"


def check_ros2_distro():
    distro = os.environ.get('ROS_DISTRO', '')
    if distro:
        return True, distro
    return False, "ROS_DISTRO 없음 — source /opt/ros/humble/setup.bash 필요"


def check_pkg(pkg_name, install_cmd):
    try:
        result = subprocess.run(
            ["ros2", "pkg", "list"],
            capture_output=True, text=True, timeout=10
        )
        if pkg_name in result.stdout:
            return True, "설치됨"
        return False, f"미설치 — {install_cmd}"
    except FileNotFoundError:
        return False, "ros2 명령 없음 (source /opt/ros/humble/setup.bash 필요)"
    except subprocess.TimeoutExpired:
        return False, "타임아웃"


def main():
    print("=" * 55)
    print(" ND1 M8 — 실습 환경 사전 검증")
    print("=" * 55)
    print()

    items = [
        ("[1/6] Python 버전",        lambda: check_python()),
        ("[2/6] ROS2 환경 (distro)", lambda: check_ros2_distro()),
        ("[3/6] TurtleBot4 시뮬",   lambda: check_pkg(
            "turtlebot4", "sudo apt install ros-humble-turtlebot4-simulator")),
        ("[4/6] SLAM Toolbox",       lambda: check_pkg(
            "slam_toolbox", "sudo apt install ros-humble-slam-toolbox")),
        ("[5/6] Nav2 (nav2_bringup)",lambda: check_pkg(
            "nav2_bringup", "sudo apt install ros-humble-navigation2")),
        ("[6/6] m8_robot 패키지",   lambda: check_pkg(
            "m8_robot",
            "cd ~/ros2_ws && colcon build --packages-select m8_robot && source install/setup.bash")),
    ]

    results = []
    for label, fn in items:
        ok, detail = fn()
        icon = "✅" if ok else "❌"
        print(f"  {icon} {label}: {detail}")
        results.append(ok)

    passed = sum(results)
    total  = len(results)
    print()
    print("=" * 55)
    if passed == total:
        print(f"✅ {passed}/{total} 모두 통과 — 실습 준비 완료!")
        print("   bash run.sh cp1 명령으로 시작하세요.")
    else:
        print(f"⚠  {passed}/{total} 통과 — 위 ❌ 항목을 먼저 해결하세요.")
        print("   RUNBOOK.md 섹션 6 (주요 오류 대응) 참조")
    print("=" * 55)


if __name__ == "__main__":
    main()
