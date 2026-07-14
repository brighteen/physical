#!/usr/bin/env python3
from __future__ import annotations
import argparse, math, time

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--x', type=float, default=0.0)
    ap.add_argument('--y', type=float, default=0.0)
    ap.add_argument('--yaw', type=float, default=0.0)
    ap.add_argument('--frame', default='map')
    args = ap.parse_args()
    rclpy.init()
    node = rclpy.create_node('nd3_initial_pose_pub')
    pub = node.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
    msg = PoseWithCovarianceStamped()
    msg.header.frame_id = args.frame
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.pose.pose.position.x = args.x
    msg.pose.pose.position.y = args.y
    msg.pose.pose.position.z = 0.0
    msg.pose.pose.orientation.z = math.sin(args.yaw / 2.0)
    msg.pose.pose.orientation.w = math.cos(args.yaw / 2.0)
    cov = [0.0] * 36
    cov[0] = 0.25
    cov[7] = 0.25
    cov[35] = 0.0685
    msg.pose.covariance = cov
    for _ in range(5):
        msg.header.stamp = node.get_clock().now().to_msg()
        pub.publish(msg)
        rclpy.spin_once(node, timeout_sec=0.1)
        time.sleep(0.2)
    print(f"Published initial pose: x={args.x}, y={args.y}, yaw={args.yaw}, frame={args.frame}")
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
