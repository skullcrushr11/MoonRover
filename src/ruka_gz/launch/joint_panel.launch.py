#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Get the launch directory
    ruka_gz_dir = get_package_share_directory('ruka_gz')

    # Define our arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Create a joint state publisher GUI node specifically for controlling robot joints
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_control_panel',
        parameters=[{
            'use_sim_time': use_sim_time,
            # Specify all arm and gripper joints explicitly
            'joints': [
                'base_link__link_01',
                'link_01__link_02',
                'link_02__link_03',
                'link_03__link_04',
                'link_04__link_05',
                'link_05__link_06',
                'link_hand_cyl__first_fin',
                'link_hand_cyl__second_fin',
            ],
            'source_list': [],  # Empty source list means the GUI will generate its own values
            'rate': 30,
            'publish_default_positions': True,
            'publish_default_velocities': True,
            'publish_default_efforts': True,
        }],
        output='screen',
        remappings=[
            # Remap to a different topic to avoid conflict with existing joint states
            ('/joint_states', '/joint_control_panel/joint_states')
        ],
    )

    # Create launch description
    ld = LaunchDescription()

    # Add argument declarations
    ld.add_action(DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    ))

    # Add nodes to launch description
    ld.add_action(joint_state_publisher_gui_node)

    return ld
