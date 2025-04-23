from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit, OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    # Launch Arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default=False)
    package_name = 'ruka_gz'

    rviz_config_arg = DeclareLaunchArgument(
        "rviz_config",
        default_value="moveit.rviz",
        description="RViz configuration file",
    )

    # sim_time = DeclareLaunchArgument(
    #    "use_sim_time",
    #     default_value= "True",
    #     description="RViz configuration file",
    # )

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution(
                [FindPackageShare('ruka_gz'),
                 'config', 'ruka_gz.urdf.xacro']
            ),
        ]
    )
    robot_description = {'robot_description': robot_description_content}

    moveit_config = (
        MoveItConfigsBuilder("ruka_gz", package_name="ruka_gz")

        .robot_description_semantic(file_path="config/ruka_gz.srdf")
        .planning_scene_monitor(
            publish_robot_description=True, publish_robot_description_semantic=True
        )
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_pipelines(
            pipelines=["chomp", "pilz_industrial_motion_planner"]
        )
        # .moveit_config_dict.update({'use_sim_time' : True})
        .to_moveit_configs()
    )


    move_group_path = os.path.join(get_package_share_directory(package_name), 'config', 'move_group.yaml')

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_config.to_dict(),
                    # moveit_config.update,
                    move_group_path],
        arguments=["--ros-args", "--log-level", "info"],
    )

    # RViz
    rviz_base = LaunchConfiguration("rviz_config")
    rviz_config = PathJoinSubstitution(
        [FindPackageShare("ruka_gz"), "config", rviz_base]
    )

    # rviz_config = PathJoinSubstitution(
    #     [FindPackageShare("ruka"), "config", "moveit.rviz"]
    # )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[
            # moveit_config.robot_description,
            robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.planning_pipelines,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            move_group_path
        ],

    )



    static_tf_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "world", "base_link"],
    )




    robot_controllers = os.path.join(get_package_share_directory(package_name), 'config', 'shok_controllers.yaml')


    # hand_controllers = os.path.join(get_package_share_directory(package_name), 'config', 'hand_controllers.yaml')

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description,
                    move_group_path] #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    )

    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description', '-name',
                   'ruka_gz', '-allow_renaming', 'false'],
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            "joint_state_broadcaster",
        ],
    )

    joint_trajectory_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'ruka_arm_controller',
            '--param-file',
            robot_controllers,
            ],
    )

    ruka_hand_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["ruka_hand_controller",
                   '--param-file',
        robot_controllers,],
    )

    # Add a node to publish the gripper joint states even if the controller isn't running
    gripper_joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[{
            'source_list': ['/joint_states'],  # Listen to the main joint states topic
            'joints': ['link_hand_cyl__first_fin', 'link_hand_cyl__second_fin'],
            'rate': 30,
            'publish_default_positions': True,
            'publish_default_velocities': True,
            'publish_default_efforts': True,
        }],
    )

    gazebo_ros_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[
            {'config_file': os.path.join(get_package_share_directory('ruka_gz'), 'config', 'ros_gz_bridge.yaml')},
        ]
    )




    world_sdf = os.path.join(get_package_share_directory('ruka_gz'), 'world', 'ruka_world.sdf')

    return LaunchDescription([

        rviz_config_arg,
        #move_group_node,  # Removing it from here
        #rviz_node,
        static_tf_node,
        gazebo_ros_bridge,

        node_robot_state_publisher,
        gripper_joint_state_publisher,  # Add the gripper joint state publisher
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [PathJoinSubstitution([FindPackageShare('ros_gz_sim'),
                                       'launch',
                                       'gz_sim.launch.py'])]),
            launch_arguments=[('gz_args', [' -r -v 4 empty.sdf --physics-engine gz-physics-bullet-featherstone-plugin'])]),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=gz_spawn_entity,
                on_exit=[joint_state_broadcaster_spawner],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[joint_trajectory_controller_spawner],
            )
        ),
        gz_spawn_entity,
        # Launch Arguments
        # DeclareLaunchArgument(
        #     name='use_sim_time',
        #      value=True
        #   ),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value=use_sim_time,
            description='If true, use simulated clock'),

        # Starting controllers first, then MoveIt after the controllers are ready
        joint_trajectory_controller_spawner,
        ruka_hand_controller_spawner,

        # Add delay before starting MoveIt to ensure gripper states are published
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=ruka_hand_controller_spawner,
                on_exit=[move_group_node],
            )
        ),

        # Start RViz after MoveIt
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=move_group_node,
                on_exit=[rviz_node],
            )
        ),

        # Removing problematic event handlers
        # RegisterEventHandler(
        #     event_handler=OnProcessExit(
        #         target_action=joint_trajectory_controller_spawner,
        #         on_exit=[ruka_hand_controller_spawner],
        #     )
        # ),
        # RegisterEventHandler(
        #     event_handler=OnProcessExit(
        #         target_action=ruka_hand_controller_spawner,
        #         on_exit=[move_group_node, rviz_node],
        #     )
        # ),
        # RegisterEventHandler(
        #     event_handler=OnProcessExit(
        #         target_action=gz_spawn_entity,
        #         on_exit=[],
        #     )
        # )


    #    rviz_node
    ])
