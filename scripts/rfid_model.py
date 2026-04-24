#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry
from math import atan2, sqrt, pow
import time
import math
from std_msgs.msg import Bool,Float64
from control_msgs.msg import JointControllerState

class tag:
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.iden = 0
    
    def distance_from_rfid(self,point):
        #print(sqrt(pow(self.x-point.x,2)+pow(self.y-point.y,2)+pow(self.z-point.z,2)))
        return sqrt(pow(self.x-point.x,2)+pow(self.y-point.y,2)+pow(self.z-point.z,2))

class RfidModel:   
    def __init__(self):
        rospy.init_node('rfid_model', anonymous=True)
        
        # Initialize subscriber to get setpoint coordinates
        rospy.Subscriber("/odom",Odometry,self.odometry_callback)
        rospy.Subscriber("/trixy/rfid_slider_controller/state",JointControllerState,self.state_callback)
        timer = rospy.Timer(rospy.Duration(0.1), self.timer_callback)
        self.tags =[]
        self.scanned_rfid=[]
        self.y_coord = [1.58,1.58,1.58,1.89,1.89,1.89,2.34,2.34,2.34,2.64,2.64,2.64,2.95,2.95,2.95,3.25,3.25,3.25,3.55,3.55,3.55,3.85,3.85,3.85,4.15,4.15,4.15,4.45,4.45,4.45]
        self.x_coord = [0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23,0.23]
        self.z_coord = [0.7,1.0,1.3,0.7,1.0,1.3,0.7,1.0,1.3,0.7,1.0,1.3,0.7,1.0,1.3,0.7,1.0,1.3,0.7,1.0,1.3,0.7,1.0,1.3,0.7,1.0,1.3,0.7,1.0,1.3]       
        self.velocity_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        for i in range(len(self.x_coord)):
            q = tag()
            q.x = self.x_coord[i]
            q.y = self.y_coord[i]
            q.z = self.z_coord[i]
            q.iden = i
            self.tags.append(q)
        self.rfid_pos = Point()
        
        # Set the rate for publishing
        self.rate = rospy.Rate(10)  # 10hz
        
    def state_callback(self,msg):
        self.rfid_pos.z = 0.6+msg.process_value
    def odometry_callback(self,msg):
        self.rfid_pos.x = msg.pose.pose.position.x
        self.rfid_pos.y = msg.pose.pose.position.y
    def timer_callback(self,msg):
        for q in self.tags:
            if q.distance_from_rfid(self.rfid_pos)<0.57:
                self.scanned_rfid.append('RFID'+str(q.iden+1))
                self.tags.remove(q)
        print("Detected Tags")
        print(self.scanned_rfid)
        
        
    
                
        time.sleep(1.0)
if __name__ == '__main__':
    try:
        RfidModel()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

