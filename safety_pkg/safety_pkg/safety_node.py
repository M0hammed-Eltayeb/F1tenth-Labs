#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import numpy as np
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from ackermann_msgs.msg import AckermannDriveStamped

class SafetyNode(Node):
    def __init__(self):
        super().__init__('safety_node')
        
        # We need to store the current speed to calculate TTC
        self.v = 0.0

        # Subscriptions
        # 1. Odometry: Topic name as per simulation requirements
        self.odom_sub = self.create_subscription(Odometry, '/ego_racecar/odom', self.odom_callback, 10)
        # 2. LaserScan: The raw Lidar data
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        # Publisher
        # To brake, we publish speed 0.0 to the /drive topic
        self.drive_pub = self.create_publisher(AckermannDriveStamped, '/drive', 10)

    def odom_callback(self, msg):
        # Update current longitudinal velocity
        self.v = msg.twist.twist.linear.x

    def scan_callback(self, scan_msg):
        # Convert ranges to a numpy array for efficient calculation
        ranges = np.array(scan_msg.ranges)
        
        # Calculate the angle for every beam in the scan
        angles = np.linspace(scan_msg.angle_min, scan_msg.angle_max, len(ranges))

        # --- TTC CALCULATION ---
        # 1. Calculate closing velocity for each beam: v_closing = v * cos(theta)
        v_closing = self.v * np.cos(angles)
        
        # 2. Only consider beams where we are moving toward the object (v_closing > 0)
        # We use a very small number (1e-9) to avoid division by zero
        v_closing_safe = np.maximum(v_closing, 1e-9)
        
        # 3. Calculate iTTC = range / closing_velocity
        ttc_array = ranges / v_closing_safe

        # --- DATA CLEANING & FILTERING ---
        # Set TTC to Infinity for:
        # - Beams where we are moving away (v_closing was <= 0)
        # - Invalid readings (NaN)
        ttc_array[v_closing <= 0] = np.inf
        ttc_array[np.isnan(ttc_array)] = np.inf
        
        # Only look at the front arc of the car (-90 to +90 degrees)
        # Objects behind the car don't affect forward AEB
        ttc_array[np.abs(angles) > (np.pi / 2)] = np.inf

        # --- DECISION ---
        # Find the smallest TTC value among all 1080 beams
        min_ttc = np.min(ttc_array)

        # If any beam indicates a collision in less than 0.45 seconds, engage brakes
        if min_ttc < 0.45:
            self.get_logger().warn(f"EMERGENCY BRAKE ENGAGED! Min TTC: {min_ttc:.3f}s")
            self.apply_brake()

    def apply_brake(self):
        # Create and publish a message with speed 0.0
        brake_msg = AckermannDriveStamped()
        brake_msg.drive.speed = 0.0
        self.drive_pub.publish(brake_msg)

def main(args=None):
    rclpy.init(args=args)
    node = SafetyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
