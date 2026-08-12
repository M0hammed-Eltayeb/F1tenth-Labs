#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from ackermann_msgs.msg import AckermannDriveStamped

class Relay(Node):
    def __init__(self):
        super().__init__('relay')
        self.subscription = self.create_subscription(
            AckermannDriveStamped, 'drive', self.drive_callback, 10)
        self.publisher_ = self.create_publisher(AckermannDriveStamped, 'drive_relay', 10)

    def drive_callback(self, msg):
        new_msg = AckermannDriveStamped()
        new_msg.drive.speed = msg.drive.speed * 3.0
        new_msg.drive.steering_angle = msg.drive.steering_angle * 3.0
        self.publisher_.publish(new_msg)

def main(args=None):
    rclpy.init(args=args)
    node = Relay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
