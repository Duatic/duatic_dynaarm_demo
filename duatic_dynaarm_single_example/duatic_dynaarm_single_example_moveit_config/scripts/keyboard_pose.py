import sys
import tty
import termios
from threading import Thread

import rclpy
from rclpy.node import Node
from rclpy.publisher import Publisher
import tf2_ros
import tf2_geometry_msgs

from geometry_msgs.msg import PoseStamped

from controller_manager_msgs.srv import SwitchController

abort_loop: bool = False


def read_char() -> int:

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def input_task(node: Node, publisher: Publisher, tf_buffer: tf2_ros.Buffer):

    while not abort_loop:

        current_pose_in_base = PoseStamped()
        current_pose_in_base.header.frame_id = "flange"

        input = read_char()
        print(ord(input))
        if ord(input) == 3:
            raise KeyboardInterrupt()

        # current_pose_in_base = tf_buffer.transform(current_pose_in_base, "base")

        pose = current_pose_in_base
        pose.header.stamp.sec = 0
        pose.header.stamp.nanosec = 0

        step = 0.002

        if input == "a":
            pose.pose.position.x = -step

        if input == "d":
            pose.pose.position.x = +step

        if input == "y":
            pose.pose.position.y = -step

        if input == "x":
            pose.pose.position.y = +step

        if input == "w":
            pose.pose.position.z = +step

        if input == "s":
            pose.pose.position.z = -step

        # pose = tf_buffer.transform(pose, "flange")
        pose.header.stamp = node.get_clock().now().to_msg()

        print(pose)
        # Default is an empty twist
        publisher.publish(pose)


def switch_controller(node, stop_controllers, start_controllers):

    # Service Clients
    switch_client = node.create_client(SwitchController, "/controller_manager/switch_controller")
    """Switches between controllers"""
    req = SwitchController.Request()
    req.deactivate_controllers = stop_controllers
    req.activate_controllers = start_controllers
    req.strictness = SwitchController.Request.STRICT
    req.activate_asap = True

    future = switch_client.call_async(req)
    rclpy.spin_until_future_complete(node, future)


def main():
    rclpy.init()

    node = Node("keypose_pose")

    tf_buffer = tf2_ros.Buffer()
    tf_listener = tf2_ros.TransformListener(tf_buffer, node)

    switch_controller(node, ["freeze_controller"], ["cartesian_pose_controller"])

    pose_publisher = node.create_publisher(
        PoseStamped, "/cartesian_pose_controller/target_pose", 10
    )

    input_thread = Thread(target=input_task, args=(node, pose_publisher, tf_buffer))
    input_thread.start()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # abort_loop = True
        input_thread.join()


if __name__ == "__main__":
    main()
