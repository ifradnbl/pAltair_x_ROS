# Altair Phase 3: ROS 2 Turtle Assessment

Tested on **Ubuntu 24.04 (WSL2)** with **ROS 2 Jazzy**.

## Dependencies

    sudo apt install -y ros-jazzy-desktop ros-dev-tools ros-jazzy-turtlesim python3-colcon-common-extensions

Python packages used: `rclpy`, `std_msgs`, `geometry_msgs`, `turtlesim`, `std_srvs`, `launch`, `launch_ros`.

## Build

Clone this repo into the `src` folder of a workspace, then build:

    mkdir -p ~/altair_phase3_ws/src && cd ~/altair_phase3_ws/src
    git clone https://github.com/ifradnbl/pAltair_x_ROS.git altair_phase3
    source /opt/ros/jazzy/setup.bash
    cd ~/altair_phase3_ws
    colcon build --symlink-install --packages-select altair_phase3
    source install/setup.bash

Open every new terminal with:

    source /opt/ros/jazzy/setup.bash
    source ~/altair_phase3_ws/install/setup.bash

## Task 1: Rover telemetry

Node names: `mars_telemetry_publisher` and `mission_control_monitor`.
Topic: `rover_telemetry`, message type `std_msgs/msg/String` (JSON with `battery_pct`, `temperature_c`, `wheel_speed_mps`, `elapsed_s`).
The monitor prints each reading and warns when battery is below 25 %.

    ros2 run altair_phase3 telemetry_pub
    ros2 run altair_phase3 monitor

Change the starting battery or drain rate:

    ros2 run altair_phase3 telemetry_pub --ros-args -p start_battery_pct:=28.0 -p depletion_pct_per_s:=2.0

## Task 2a: Driving menu

Start turtlesim, then the menu. Commands: P (patrol), R (rectangle), Z (zigzag), Q (quit).

    ros2 run turtlesim turtlesim_node
    ros2 run altair_phase3 turtle_menu

Reset the turtle between patterns:

    ros2 service call /reset std_srvs/srv/Empty "{}"

## Task 3: Three stops before cha

Starts turtlesim and the mission node together (Bottle, then Mallet, then Base, then DONE):

    ros2 launch altair_phase3 field.launch.py

Interfaces: pose in `/turtle1/pose`, velocity out `/turtle1/cmd_vel`, blockage in `/field_blocked` (`std_msgs/msg/Bool`), resume service `/resume_mission` (`std_srvs/srv/Trigger`).
The mission node is the only publisher to `/turtle1/cmd_vel`. A block pauses it and keeps its target. Clearing the block does not resume; only a successful `/resume_mission` call does.

In a second terminal:

    ros2 topic pub --once /field_blocked std_msgs/msg/Bool "{data: true}"
    ros2 service call /resume_mission std_srvs/srv/Trigger "{}"
    ros2 topic pub --once /field_blocked std_msgs/msg/Bool "{data: false}"
    ros2 service call /resume_mission std_srvs/srv/Trigger "{}"

The first resume is rejected (still blocked); the last one succeeds.
