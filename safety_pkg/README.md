Launching the node:  
colcon build --packages-select safety_pkg --paths src/f1tenth_gym_ros/safety_pkg  
source install/setup.bash  
ros2 run safety_pkg safety_node  
