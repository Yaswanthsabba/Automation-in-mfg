#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry
from math import atan2, sqrt, pow
from control_msgs.msg import JointControllerState
import time
import math
from std_msgs.msg import Bool,Float64

class SliderOperation:
    def __init__(self):
        rospy.init_node('slider_operation', anonymous=True)
        
        # Initialize subscriber to get setpoint coordinates
        self.position_publisher = rospy.Publisher('/trixy/rfid_slider_controller/command', Float64, queue_size=10)
        self.height = 0.2
        # Initialize publisher to publish velocity commands
        #self.velocity_publisher = rospy.Subscriber('/trixy/rfid_slider_controller/state', JointControllerState, odometry_callback)
        self.flag_pub = rospy.Publisher('/slider_flag',Bool,queue_size=10)
        rospy.Subscriber("/movement_flag",Bool,self.flag_callback)
        timer = rospy.Timer(rospy.Duration(0.2), self.timer_callback)
        self.Flag=0
        self.movement_flag=False
        # Set the rate for publishing
        self.rate = rospy.Rate(10)  # 10hz
        
    def flag_callback(self,msg):
        self.movement_flag=msg.data
        print(str(self.movement_flag))
        if self.movement_flag==True:
            self.flag_pub.publish(False)
    def timer_callback(self,event):
        if self.movement_flag==False:
            self.Flag=0
        if self.movement_flag==True:
            if self.Flag==0:
               self.height+=0.05
               if self.height>0.68:
                   self.Flag=1
               print("RISING/////////////////////////////////////////////")
               self.position_publisher.publish(self.height)
            elif self.Flag==1:
               print('FALLING////////////////////////////////////////////')
               self.height-=0.05
               self.position_publisher.publish(self.height)
               if self.height<0.22:
                   self.Flag=-1
            elif self.Flag==-1:
               self.height=0.2
               self.position_publisher.publish(self.height)
               self.Flag=2
               print("Ended")
            if self.Flag==2:
               self.flag_pub.publish(True)
    
    
if __name__ == '__main__':
    try:
        SliderOperation()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

