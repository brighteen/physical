#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
import cv2
from cv_bridge import CvBridge

class SyntheticCamera(Node):
    def __init__(self):
        super().__init__('synthetic_camera')
        # 🎯 버퍼 지연(Lag) 방지를 위해 큐 사이즈를 1로 제한하여 항상 최신 프레임만 처리하도록 설정
        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 1)
        # 🎯 로봇의 위치 기반 오인식 방지를 위한 Odom 토픽 구독
        self.odom_subscription = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        # 🎯 박스 검출 여부 및 위치를 알릴 Publisher 선언
        self.pose_publisher = self.create_publisher(PoseStamped, '/box_detected', 10)
        self.bridge = CvBridge()
        
        # 🎯 실제 가제보 모델의 마커 규격(DICT_6X6_250)으로 복구
        self.dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        
        # 💡 CLAHE: 창고 환경의 불균일 조명 및 선반 그림자 보정을 위한 적응형 히스토그램 평활화 객체
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        # 📍 로봇의 실시간 좌표
        self.robot_x = 0.0
        self.robot_y = 0.0
        
        self.get_logger().info('📸 로컬 ArUco 감지 및 Odom 게이팅 카메라 가동!')

    def odom_callback(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y

    def image_callback(self, msg):
        # 💡 [영역 필터링 적용]
        # 출발 구역 A(y: ~7.3) 근처의 수많은 선반 적재 상자들로 인한 오인식을 차단하기 위해
        # 진짜 마커 상자가 위치한 중심 구역 통로(y가 -3.0에서 2.0 사이) 내에 진입했을 때만 비전 인식을 가동합니다.
        in_target_zone = (self.robot_y > -3.0 and self.robot_y < 2.0)
        
        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        h, w, _ = img.shape

        # 화면 중앙 조준선은 원본 이미지에 표시
        cv2.line(img, (int(w/2), 0), (int(w/2), h), (255, 255, 255), 1)
        cv2.line(img, (0, int(h/2)), (w, int(h/2)), (255, 255, 255), 1)

        # 타겟 영역을 벗어난 경우 스크린 가이드만 띄우고 처리 생략
        if not in_target_zone:
            cv2.putText(img, "OUT OF DETECT ZONE (ARUCO SLEEP)", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.imshow("YOLO Data Capture - Special Camera View", img)
            cv2.waitKey(1)
            return

        # BGR → LAB 색상 공간으로 변환 후 밝기(L) 채널에만 CLAHE를 적용하여 대비 개선
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_eq = self.clahe.apply(l)
        lab_eq = cv2.merge((l_eq, a, b))
        img_detect = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)

        try:
            # 💡 모든 커스텀 튜닝을 걷어내고 순정(기본값) 파라미터로 마커를 검출합니다.
            parameters = cv2.aruco.DetectorParameters()
            detector = cv2.aruco.ArucoDetector(self.dict, parameters)
            corners, ids, _ = detector.detectMarkers(img_detect)
        except AttributeError:
            parameters = cv2.aruco.DetectorParameters_create()
            corners, ids, _ = cv2.aruco.detectMarkers(img_detect, self.dict, parameters=parameters)

        if ids is not None and len(ids) > 0:
            for i, corner in enumerate(corners):
                pts = corner[0].astype(int)
                x_min, y_min = pts[:, 0].min(), pts[:, 1].min()
                x_max, y_max = pts[:, 0].max(), pts[:, 1].max()

                # 바운딩 박스 오버레이
                cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
                label = f"ArUco_ID_{ids[i][0]}"
                cv2.putText(img, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                # YOLO 상대 크기 계산
                nw = (x_max - x_min) / w
                nh = (y_max - y_min) / h
                cx = ((x_min + x_max) / 2) / w
                cy = ((y_min + y_max) / 2) / h
                self.get_logger().info(f"💾 [라벨링 데이터] {ids[i][0]} {cx:.4f} {cy:.4f} {nw:.4f} {nh:.4f}")

                # 🎯 진짜 상자의 마커 ID(0 ~ 5)이고 크기가 5% 이상일 때만 우회 트리거 발행
                if ids[i][0] in [0, 1, 2, 3, 4, 5] and nw > 0.05:
                    pose_msg = PoseStamped()
                    pose_msg.header.frame_id = 'map'
                    pose_msg.header.stamp = self.get_clock().now().to_msg()
                    
                    # 가제보 상의 aruco_box 위치(x: 1.02057, y: -0.588931)로 안전하게 다가가기 위한 목적지 좌표 설정
                    pose_msg.pose.position.x = 1.02057
                    pose_msg.pose.position.y = -1.1
                    pose_msg.pose.position.z = 0.0
                    pose_msg.pose.orientation.z = 0.707
                    pose_msg.pose.orientation.w = 0.707
                    
                    self.pose_publisher.publish(pose_msg)
                    self.get_logger().info(f"🎯 [ArUco 감지] 타겟 마커(ID:{ids[i][0]}) 확인! 동적 우회 주행 좌표 발행 완료!")

        cv2.imshow("YOLO Data Capture - Special Camera View", img)
        cv2.waitKey(1)

def main():
    rclpy.init()
    rclpy.spin(SyntheticCamera())
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()