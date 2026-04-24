#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry
from math import atan2, sqrt, pow
import time
import math
from std_msgs.msg import Bool,Float64

class PathPlanner:
    def __init__(self):
        rospy.init_node('path_planner', anonymous=True)
        
        # Initialize subscriber to get setpoint coordinates
        self.setpoint_pub = rospy.Publisher("/setpoint", Point, queue_size=10)
        #rospy.Subscriber("/odom",Odometry,self.odometry_callback)
        rospy.Subscriber("/setpoint_received_flag",Bool,self.received_callback)
        self.setpoint_sent_pub=rospy.Publisher("/setpoint_sent_flag",Bool,queue_size=10)
        self.received_flag=True
        # Initialize publisher to publish velocity commands
        #self.velocity_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        #self.movement_flag_pub = rospy.Publisher('/movement_flag',Bool,queue_size=10)
        
        # Initialize variables
        self.x_coord = [0.7,0.7,0.7,0.7,0.7,0.7,0.7,0.7,0.7,0.7]
        self.y_coord = [1.64,1.94,2.24,2.54,2.74,3.04,3.34,3.64,3.94,4.24]
        self.z_coord = [0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4]
        #self.x_coord = [0.91,2.69,2.67,0.85]
        #self.y_coord = [4.08,4.08,0.71,0.75]
        #self.z_coord = [0.4,0.4,0.4,0.4]
        self.path = []
        self.index=0
        for i in range(len(self.x_coord)):
            q = Point()
            q.x=self.x_coord[i]
            q.y=self.y_coord[i]
            q.z=self.z_coord[i]
            self.path.append(q)
        timer = rospy.Timer(rospy.Duration(0.1), self.timer_callback)
        
    def received_callback(self,msg):
        self.received_flag = msg.data
    def timer_callback(self,event):
        if self.received_flag==True:
            self.setpoint_pub.publish(self.path[self.index])
            self.index+=1
            self.setpoint_sent_pub.publish(True)
        else:
            print("waiting/////////////////////////////////")
        
       
        
       
   
    
if __name__ == '__main__':
    try:
        PathPlanner()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

