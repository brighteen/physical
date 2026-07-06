#!/usr/bin/env python3
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped
import time

# 🎯 BasicNavigator를 직접 상속받아 단일 노드 안에서 구독과 주행을 통합 처리
class WafflePiNavigator(BasicNavigator):
    def __init__(self):
        super().__init__('waffle_pi_navigator')
        
        # 시나리오 제어 변수들
        self.box_pose = None
        self.box_detected = False
        self.has_box = False
        self.is_diverted = False
        
        # 🎯 마커 감지 구독자를 노드에 직접 바인딩
        self.subscription = self.create_subscription(
            PoseStamped,
            '/box_detected',
            self.box_detected_callback,
            10
        )
        self.get_logger().info('⚓ Waffle Pi 통합 자율주행 제어 노드 가동 완료!')

    def box_detected_callback(self, msg):
        if not self.has_box and not self.is_diverted:
            self.box_pose = msg
            self.box_detected = True
            self.is_diverted = True
            self.get_logger().info('🚨 [경고] 경로 상에 ArUco 마커 박스가 감지되었습니다! 박스로 우회합니다.')

def main():
    rclpy.init()
    
    # 🎯 단일 통합 노드로 인스턴스 생성
    navigator = WafflePiNavigator()
    
    print("Nav2 시스템이 활성화될 때까지 대기합니다...")
    navigator.waitUntilNav2Active()
    
    # ==========================================
    # [1] A 지점 목표 좌표 설정 (상자 적재 구역)
    # ==========================================
    goal_a = PoseStamped()
    goal_a.header.frame_id = 'map'
    goal_a.header.stamp = navigator.get_clock().now().to_msg()
    goal_a.pose.position.x = 0.29974666237831116
    goal_a.pose.position.y = 7.338226795196533
    goal_a.pose.orientation.z = 0.0
    goal_a.pose.orientation.w = 1.0

    # ==========================================
    # [2] B 지점 목표 좌표 설정 (최종 하역 구역)
    # ==========================================
    goal_b = PoseStamped()
    goal_b.header.frame_id = 'map'
    goal_b.header.stamp = navigator.get_clock().now().to_msg()
    goal_b.pose.position.x = -2.0569841861724854
    goal_b.pose.position.y = -3.1936516761779785
    goal_b.pose.orientation.z = 0.0
    goal_b.pose.orientation.w = 1.0

    try:
        # 1단계: A 지점으로 이동
        print("\n[Step 1] 로봇이 A 지점으로 출발합니다.")
        navigator.goToPose(goal_a)
        
        # 단일 스레드 환경에서 콜백 수신을 유도하기 위해 spin_once를 호출하는 루프
        while not navigator.isTaskComplete():
            rclpy.spin_once(navigator, timeout_sec=0.1)
            
        print("\n✨ A 지점 도착 완료! B 지점으로 출발합니다.")
        time.sleep(1)

        # 2단계: B 지점으로 출발
        print("\n[Step 2] 로봇이 B 지점으로 출발합니다. (주행 중 마커 감지 감시 중)")
        navigator.goToPose(goal_b)
        
        # B 지점으로 가는 도중 마커 감지 이벤트를 계속 체크하는 루프
        diverted = False
        while not navigator.isTaskComplete():
            # 콜백 대기용 스핀 수행
            rclpy.spin_once(navigator, timeout_sec=0.05)
            
            if navigator.box_detected and not navigator.has_box:
                print("\n⚠️ [이벤트 발생] 주행 도중 ArUco 마커 박스 감지! 기존 주행을 취소하고 박스로 접근합니다.")
                navigator.cancelTask()  # 기존 B 지점 주행 취소
                diverted = True
                break
                
            time.sleep(0.05)

        # 3단계: 박스 위치로 우회 이동 (우회 이벤트가 발동했을 때만 실행)
        if diverted:
            print(f"[Step 3] 박스 목적지(x: {navigator.box_pose.pose.position.x:.2f}, y: {navigator.box_pose.pose.position.y:.2f})로 출발합니다.")
            navigator.goToPose(navigator.box_pose)
            
            while not navigator.isTaskComplete():
                rclpy.spin_once(navigator, timeout_sec=0.1)
                
            print("\n📦 박스 근처 도착 완료! (하드코딩: 박스 적재 중... 3초 대기)")
            time.sleep(3)
            print("✨ 박스 적재 성공!")
            navigator.has_box = True
            
            # 4단계: 적재 완료 후 최종 목적지인 B 지점으로 재출발
            print("\n[Step 4] 박스를 싣고 최종 목적지 B 지점으로 재출발합니다.")
            navigator.goToPose(goal_b)
            while not navigator.isTaskComplete():
                rclpy.spin_once(navigator, timeout_sec=0.1)
            
        print("\n✨ 최종 목적지 B 지점 도착 완료! 물류 이송 시나리오를 종료합니다.")

    except KeyboardInterrupt:
        print("\n사용자에 의해 미션이 중단되었습니다.")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
