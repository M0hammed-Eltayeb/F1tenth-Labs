import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    config = os.path.join(
        get_package_share_directory('lab1_pkg'),
        'config',
        'params.yaml'
    )

    
    talker_node = Node(
        package='lab1_pkg',
        executable='talker.py',
        name='talker',
        parameters=[config]  
    )

    
    relay_node = Node(
        package='lab1_pkg',
        executable='relay.py',
        name='relay'
    )


    return LaunchDescription([
        talker_node,
        relay_node
    ])
