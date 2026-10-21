Altair Phase 3

__Build___
source /opt/ros/humble/setup.bash
cd ~/altair_phase3_ws && colcon build --symlink-install --packages-select altair_phase3
source install/setup.bash

___Run___
ros2 run altair_phase3 mars_telemetry_publisher
ros2 run altair_phase3 mission_control_monitor
ros2 run altair_phase3 turtle_menu          # needs turtlesim_node running
ros2 launch altair_phase3 field.launch.py   # starts turtlesim + mission node
The launch command starts turtlesim and mission_node together.

Resume after a block: ros2 service call /resume_mission std_srvs/srv/Trigger "{}"
