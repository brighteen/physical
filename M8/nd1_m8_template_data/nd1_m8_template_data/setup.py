from setuptools import setup, find_packages

package_name = 'm8_robot'

setup(
    name=package_name,
    version='1.1.0',
    packages=find_packages(exclude=['test', 'tests']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            [f'resource/{package_name}']),
        (f'share/{package_name}', ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ND1 Student',
    maintainer_email='student@nd1.ac.kr',
    description='ND1 M8 — ROS2 기초 및 로봇 시스템 통합 실습 패키지',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # CP0: TurtleSim 사각형 이동 (워밍업)
            'square_mover = m8_robot.cp0_square_mover:main',

            # CP1: robot_mover → TODO 3개 실습 과제 (30점)
            'robot_mover  = m8_robot.cp1_robot_mover:main',

            # CP1 심화: LaserScan 이상치 필터링 + RViz2 시각화 (가산점 +4점)
            'sensor_filter = m8_robot.cp1_5_sensor_filter:main',

            # CP2: SLAM 지도 생성 + 커버리지 모니터 (30점)
            'slam_mapper = m8_robot.cp2_slam_mapper:main',

            # CP3: nav2_client → TODO 2개 실습 과제 (40점)
            'cp3_nav2_client = m8_robot.cp3_nav2_client:main',

            # M7→M8 브릿지 (M7 IK → JointState/JointTrajectory)
            'm7_to_ros2_bridge = m8_robot.m7_to_ros2_bridge:main',
        ],
    },
)
