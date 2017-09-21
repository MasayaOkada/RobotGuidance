#!/usr/bin/env python
# check node
# rostopic pub -1 /adc rosserial_arduino/Adc 0 0 0 0 0 0

import rospy
from std_msgs.msg import Float32
from rosserial_arduino.msg import Adc
import time

class guidance_reward:
	def __init__(self):
		rospy.init_node('guidance_reward', anonymous=True)
		self.poten_sub = rospy.Subscriber("/adc", Adc, self.callback_poten)
		self.reward_pub = rospy.Publisher('/reward', Float32, queue_size=10)
		self.action = 0
		self.poten = Adc()
		self.pitch = 0
		self.yaw = 0

	def callback_poten(self, data):
		self.poten = data
#		self.reward = 2.0 - (self.poten.adc0 + self.poten.adc1 + self.poten.adc2 * 2 + self.poten.adc3 * 2) / 100.0
				
		self.reward = 0;		
#		yaw = self.poten.adc0 + self.poten.adc1;
#		if ((yaw <= 5) or ((yaw - self.yaw) < 0)):
#			self.reward += 1
#		self.yaw = yaw

#		pitch = self.poten.adc2 + self.poten.adc3
#		if ((pitch <= 5) or (pitch - self.pitch) < 0):
#			self.reward += 1
#		self.pitch = pitch

#		self.reward = 10.0 - (self.poten.adc2 + self.poten.adc3)/45.0*20
		self.reward_fb = 1.0 - (self.poten.adc2 + self.poten.adc3)/15.0
		self.reward_lr = 1.0 - (self.poten.adc0 + self.poten.adc1)/30.0
		self.reward = self.reward_fb ** 3 + self.reward_lr ** 3

		print 'LR = ', round(self.reward_lr, 2), ' \tBF = ', round(self.reward_fb, 2), '\treward = ', round(self.reward, 2)

		#Publish the velocity
		self.reward_pub.publish(self.reward)

if __name__ == '__main__':
	gr = guidance_reward()
	try:
		rospy.spin()
	except KeyboardInterrupt:
		print("Shutting Down")
