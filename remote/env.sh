#!/bin/sh

export ROS_MASTER_URI="http://$1.local:11311"
export ROS_IP="lab.local"
set -x
shift
(cd /opt/ros/kinetic && ./env.sh "$@")
