#!/usr/bin/env python3
from __future__ import annotations
import argparse, math, sys

import rclpy
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--x', type=float, required=True)
    ap.add_argument('--y', type=float, required=True)
    ap.add_argument('--yaw', type=float, default=0.0)
    ap.add_argument('--frame', default='map')
    ap.add_argument('--timeout', type=float, default=120.0)
    args = ap.parse_args()

    rclpy.init()
    node = rclpy.create_node('nd3_send_goal')
    try:
        client = ActionClient(node, NavigateToPose, 'navigate_to_pose')
        if not client.wait_for_server(timeout_sec=10.0):
            print('NavigateToPose action server not available', file=sys.stderr)
            sys.exit(2)

        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = args.frame
        goal.pose.header.stamp = node.get_clock().now().to_msg()
        goal.pose.pose.position.x = args.x
        goal.pose.pose.position.y = args.y
        goal.pose.pose.orientation.z = math.sin(args.yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(args.yaw / 2.0)

        print(f'Sending goal: x={args.x}, y={args.y}, yaw={args.yaw}, frame={args.frame}')
        fut = client.send_goal_async(goal)
        rclpy.spin_until_future_complete(node, fut, timeout_sec=10.0)
        if not fut.done():
            print('Goal request timeout', file=sys.stderr)
            sys.exit(2)

        handle = fut.result()
        if not handle.accepted:
            print('Goal rejected by server', file=sys.stderr)
            sys.exit(3)

        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(node, result_future, timeout_sec=args.timeout)
        if not result_future.done():
            print('Goal timeout; cancel requested', file=sys.stderr)
            cancel_future = handle.cancel_goal_async()
            rclpy.spin_until_future_complete(node, cancel_future, timeout_sec=5.0)
            sys.exit(4)

        status = result_future.result().status
        print(f'Goal finished with status={status}')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
