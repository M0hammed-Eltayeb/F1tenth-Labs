1-Building the work space
    cd /lab1_ws
    source /opt/ros/foxy/setup.bash
    source install/setup.bash
    colcon build --packages-select lab1_pkg
    
    
2-launching 
    ros2 launch lab1_pkg lab1_launch.py
    
    
3- verifying ( open another terminal ) 
    source /opt/ros/foxy/setup.bash
    ros2 topic echo /drive_relay
