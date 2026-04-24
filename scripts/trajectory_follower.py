#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry
from math import atan2, sqrt, pow
import time
import math
from std_msgs.msg import Bool,Float64

class DifferentialDriveController:
    def __init__(self):
        rospy.init_node('differential_drive_controller', anonymous=True)
        
        # Initialize subscriber to get setpoint coordinates
        rospy.Subscriber("/setpoint", Point, self.setpoint_callback)
        rospy.Subscriber("/odom",Odometry,self.odometry_callback)
        rospy.Subscriber("/slider_flag",Bool,self.flag_callback)
        rospy.Subscriber("/setpoint_sent_flag",Bool,self.sent_callback)
        
        # Initialize publisher to publish velocity commands
        self.velocity_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.movement_flag_pub = rospy.Publisher('/movement_flag',Bool,queue_size=10)
        self.received_setpoint_pub=rospy.Publisher("/setpoint_received_flag",Bool,queue_size=10)
        
        # Initialize variables
        self.current_position = Point()
        self.setpoint = Point()
        self.sent_flag=False
        self.received_setpoint_data = False
        timer = rospy.Timer(rospy.Duration(0.5), self.timer_callback)
        
        # Set the rate for publishing
        self.rate = rospy.Rate(10)  # 10hz
        self.slider_flag = True
        
        # Call the function to move towards setpoint
        
    def sent_callback(self,msg):
        self.sent_flag = msg.data
        self.received_setpoint_pub.publish(False)
    def flag_callback(self,msg):
        self.slider_flag=msg.data
        print(str(self.slider_flag))
        if self.slider_flag==True:
            self.movement_flag_pub.publish(False)
        
    def setpoint_callback(self, data):
        self.setpoint = data
        print("Setpoint_Recived")
        self.received_setpoint_data = True

    def odometry_callback(self, data):
        self.current_position = data.pose.pose.position
        self.current_orientation = data.pose.pose.orientation
        
    def timer_callback(self,event):
        if self.received_setpoint_data==True and self.slider_flag==True and self.sent_flag==True:
            self.move_to_setpoint()
        else:
            print("waiting for next setpoint")
        
    def quat_to_euler(self,point):
        x = point.x
        y = point.y
        z = point.z
        w = point.w
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        return yaw
        
    def move_to_setpoint(self):
        # Calculate the distance to the setpoint
        distance = sqrt(pow((self.setpoint.x - self.current_position.x), 2) +
                            pow((self.setpoint.y - self.current_position.y), 2))
        desired_angle =atan2(self.setpoint.y - self.current_position.y,
                                  self.setpoint.x - self.current_position.x)
        print(str(desired_angle))
        print(str(self.quat_to_euler(self.current_orientation)))
        # Define the velocity message
        velocity_msg = Twist()
        yaw_error = desired_angle - self.quat_to_euler(self.current_orientation)
        if yaw_error > 3.14:
            yaw_error -= 2 * 3.14
        if yaw_error < -3.14:
            yaw_error += 2 * 3.14
        if(abs(yaw_error)<0.05):
            # Define the linear velocity
            velocity_msg = Twist()
            velocity_msg.linear.x = 10*distance 
            self.velocity_publisher.publish(velocity_msg)
            print("Published translation")
            # Check if the robot reached close to the setpoint
            if distance < 0.15:
                rospy.loginfo("Reached close to the setpoint")
                velocity_msg=Twist()
                self.received_setpoint_data=False
                self.movement_flag_pub.publish(True)
                self.received_setpoint_pub.publish(True)
                self.velocity_publisher.publish(velocity_msg)
                print("ROBOT_STOPPED")
        else:
            if yaw_error>0:
                velocity_msg.angular.z = 0.5*(yaw_error)
            else:
                velocity_msg.angular.z = 0.5*(yaw_error)
            self.velocity_publisher.publish(velocity_msg)
                
if __name__ == '__main__':
    try:
        DifferentialDriveController()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

