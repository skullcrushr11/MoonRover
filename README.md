

```
sudo apt update -y && sudo apt upgrade -y
```

```
locale  

sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

locale  # verify settings
```



```
sudo apt install software-properties-common
sudo add-apt-repository universe
```



```
sudo apt update -y && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
```



```
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```



```
sudo apt update -y && sudo apt install ros-dev-tools -y
```

```
sudo apt update -y && sudo apt upgrade -y
```


```
sudo apt install ros-jazzy-desktop -y
```


```
echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc
```



```
sync
reboot
```


```
cd
git clone --recurse-submodules https://github.com/voltbro/roverchallenge-ru.git
echo "source ~/roverchallenge-ru/setup.sh" >> ~/.bashrc
```

```
sudo apt update && sudo apt upgrade && sudo apt install python3-pip jsonnet just ros-jazzy-joy ros-jazzy-ros2-control ros-jazzy-gz-ros2-control ros-jazzy-ros2-controllers ros-jazzy-ros-gz ros-jazzy-moveit ros-jazzy-moveit-planners-chomp ros-jazzy-imu-tools can-utils -y
```

```
echo "export PIP_BREAK_SYSTEM_PACKAGES=1" >> ~/.bashrc
```


```
sync
reboot
```


```
sudo rosdep init
rosdep update
```

```
rosdep install -r --from-paths . --ignore-src --rosdistro $ROS_DISTRO -y
```


```
sync
reboot
```


```
cd ~/roverchallenge-ru/
just sim
```


```
cd ~/roverchallenge-ru/
just sim
```

![Simulator_ROS2](https://github.com/user-attachments/assets/9a479dd4-403d-4034-8b4d-8b78eca259ab)
