#!/usr/bin/env python
from __future__ import print_function
import roslib
roslib.load_manifest('robot_guidance')
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import Float32, Int8
import numpy as np

class dummy_robot:
    def __init__(self):
        rospy.init_node('dummy_robot', anonymous=True)
        self.bridge = CvBridge()
        self.image_pub = rospy.Publisher("image_raw", Image, queue_size=1)
        self.reward_pub = rospy.Publisher("reward", Float32, queue_size=1)
        self.action_sub = rospy.Subscriber("action", Int8, self.callback_action)
        self.action = 0
        self.pan = 0
        self.size = 0
        self.reward = 0
        self.reward_lr = 0
        self.reward_fb = 0
        self.cv_image = np.zeros((480,640,3), np.uint8)
        self.cv_image.fill(255)
        self.image = self.bridge.cv2_to_imgmsg(self.cv_image, encoding="bgr8")
        self.arrow_cv_image = np.zeros((200,640,3), np.uint8)
        self.arrow_cv_image.fill(255)
        self.image_timer = rospy.Timer(rospy.Duration(0.033), self.callback_image_timer)
        self.reward_timer = rospy.Timer(rospy.Duration(0.05), self.callback_reward_timer)
        self.count = 0
        self.prev_count = -1

    def callback_image_timer(self, data):
        self.cv_image.fill(255)
        cv2.circle(self.cv_image, (640 / 2 + self.pan, 480 / 2),  100 + self.size, (0, 255, 0), -1)
        self.image = self.bridge.cv2_to_imgmsg(self.cv_image, encoding="bgr8")
        self.image_pub.publish(self.image)

    def callback_action(self, data):
        action_list = [[0, 2], [-10, 0], [10, 0], [0, 0]]
        self.action = data.data
        if (self.action < 0 or self.action >= 5):
            return
        self.pan += action_list[self.action][0]
        self.size += action_list[self.action][1]
        if self.size < -50:
            self.size = -50
        elif self.size > 50:
            self.size = 50
        if self.pan < -250:
            self.pan = -250
        elif self.pan > 250:
            self.pan = 250
        self.count += 1
        if ((self.count % 100) == 0):
            self.pan = int(np.random.rand() * 400 - 200)
#            self.size = int(np.random.rand() * 100 - 50)
            self.size = int(np.random.rand() * 50 - 50)
            print("change pan angle && circle size")

        pt1 = (320, 100)
        if (self.action == 1):
            pt2 = (320-200, 100)
        elif (self.action == 2):
            pt2 = (320+200, 100)
        elif (self.action == 3):
            pt2 = (320, 100)
        else:
            pt2 = (320, 100 - 50)

        self.arrow_cv_image.fill(255)
        cv2.line(self.arrow_cv_image, pt1, pt2, (0,0,200), 10)
        cv2.imshow("action", self.arrow_cv_image)
        cv2.waitKey(1)

    def callback_reward_timer(self, data):
        if (self.prev_count == self.count):
            print("reward timer is too fast!")
        self.prev_count = self.count
        self.reward_lr = min(1.0 - abs(self.pan) / 100.0, 1.0)
        self.reward_fb = min(1.0 - abs(self.size) / 25.0, 1.0)
        self.reward_lr = self.reward_lr ** 3 - 1
        self.reward_fb = self.reward_fb ** 3 - 1
        self.reward = self.reward_lr + self.reward_fb
#        print("selected_action: " + str(self.action) + ", reward: " + str(self.reward))
        self.reward_pub.publish(self.reward)

if __name__ == '__main__':
    dr = dummy_robot()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting Down")
cv2.destroyAllWindows()
