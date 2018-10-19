#!/usr/bin/env python

import rospy
import mavros
import threading
from mavros import command
from mavros_msgs.msg import State
from mavros_msgs.srv import SetMode, SetModeRequest
from sensor_msgs.msg import Joy

from mavros.utils import *

class AeroOffboard:
  def __init__(self):
    rospy.Subscriber("/joy", Joy, self.joy_cb)
    self.DISARMED = 1
    self.OFFBOARD = 2
    self.ARMED = 3
    self.state_mach = self.DISARMED

  def set_offboard_mode(self):
      done_evt = threading.Event()
      def state_cb(state):
          if state.armed:
              self.state_mach = self.ARMED
              rospy.loginfo("Drone armed!")
          elif state.mode == "OFFBOARD":
              self.state_mach = self.OFFBOARD
              rospy.loginfo("Drone in OFFBOARD mode!")
              done_evt.set()
          else:
              self.state_mach = self.DISARMED
              rospy.loginfo("Drone disarmed!")

      try:
          set_mode = rospy.ServiceProxy(mavros.get_topic('set_mode'), SetMode)
          ret = set_mode(custom_mode="OFFBOARD")
      except rospy.ServiceException as ex:
          fault(ex)

      sub = rospy.Subscriber(mavros.get_topic('state'), State, state_cb)

      if not ret.mode_sent:
          fault("Request failed. Check mavros logs")

      if not done_evt.wait(5):
          fault("Timed out!")

  def joy_cb(self, data):
    if self.state_mach == self.DISARMED and data.buttons[20] == 1:
      mavros.set_namespace()
      self.set_offboard_mode()
    elif self.state_mach == self.OFFBOARD and data.buttons[3] == 1:
      command.arming(True)
    elif self.state_mach == self.ARMED and data.buttons[4] == 1:
      command.arming(False)


def main():
  rospy.init_node('offboard', anonymous=True)
  AeroOffboard()
  rospy.spin()

if __name__ == '__main__':
  try:
    main()
  except rospy.ROSInterruptException:
    pass
