# Image args should come at the beginning.
ARG BASE_IMAGE
ARG PREBUILT_BASE_IMAGE
# hadolint ignore=DL3006
FROM $BASE_IMAGE as devel
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG ROS_DISTRO
ARG SETUP_ARGS

## Fix broken Ubuntu 22.04 Mesa for WSL2 Docker https://bugs.launchpad.net/ubuntu/+source/mesa/+bug/2004649
## TODO: remove/re-evaluate after Ubuntu 24.04 is released
## Fix OpenGL issues (e.g. black screen in rviz2) due to old mesa lib in Ubuntu 22.04
## See https://github.com/autowarefoundation/autoware.universe/issues/2789
# hadolint ignore=DL3008
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y software-properties-common \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y gpg-agent dirmngr gpg \
  && apt-add-repository ppa:kisak/kisak-mesa \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
  libegl-mesa0 libegl1-mesa-dev libgbm-dev libgbm1 libgl1-mesa-dev libgl1-mesa-dri libglapi-mesa libglx-mesa0

## Install apt packages

## Add uilts
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install less nano unzip iputils-ping bc

# add boost
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
  python3-numpy \
  libboost-python-dev \
  libboost-numpy-dev 

# TODO massive problem how do I solve this propeyly:
#      I want to link .sos from above but they look like: /usr/lib/x86_64-linux-gnu/libboost_numpy310.so
#      (so to build against it would need -lboost_numpy310 -lboost_python310 and -lpython3.10) so I need to lock in
#      a version here or generically search for proper version to symlink in the pythonStubGeneration script
RUN ln -s /usr/lib/x86_64-linux-gnu/libboost_numpy310.so /usr/lib/x86_64-linux-gnu/libboost_numpy.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libboost_python310.so /usr/lib/x86_64-linux-gnu/libboost_python3.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libpython3.10.so /usr/lib/x86_64-linux-gnu/libpython.so

# hadolint ignore=DL3008
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
  git \
  ssh \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

## Copy files
COPY autoware.repos setup-dev-env.sh ansible-galaxy-requirements.yaml amd64.env arm64.env /autoware/
COPY ansible/ /autoware/ansible/

RUN mkdir /autoware/src

WORKDIR /autoware
RUN ls /autoware

## Add GitHub to known hosts for private repositories
RUN mkdir -p ~/.ssh \
  && ssh-keyscan github.com >> ~/.ssh/known_hosts \
  && ssh-keyscan -p 8022 gitlab.fixstars.com >> ~/.ssh/known_hosts

## Set up development environment
RUN --mount=type=ssh \
  ./setup-dev-env.sh -y $SETUP_ARGS universe \
  && pip uninstall -y ansible ansible-core \
  && vcs import src < autoware.repos

# Patch introduced humble autoware namespace collision https://github.com/autowarefoundation/autoware.universe/pull/5089
RUN mkdir -p /autoware/patches
COPY patches/autoware_auto_tf2_humble_fix_5089.patch /autoware/patches/
COPY patches/autoware_map_loader_visualize_crosswalk_ids.patch /autoware/patches/
COPY patches/autoware_goal_planner_fix_4472.patch /autoware/patches/
COPY patches/autoware_mission_planner_routing_api_4942.patch /autoware/patches/
COPY patches/autoware_mpc_fix_4673.patch /autoware/patches/
COPY patches/llh_converter_plane_20.patch /autoware/patches/
WORKDIR /autoware/src/universe/autoware.universe
RUN patch -p1 < /autoware/patches/autoware_auto_tf2_humble_fix_5089.patch
RUN patch -p1 < /autoware/patches/autoware_map_loader_visualize_crosswalk_ids.patch
RUN patch -p1 < /autoware/patches/autoware_goal_planner_fix_4472.patch
RUN patch -p1 < /autoware/patches/autoware_mission_planner_routing_api_4942.patch
RUN patch -p1 < /autoware/patches/autoware_mpc_fix_4673.patch
WORKDIR /autoware/src/universe/external/llh_converter
RUN patch -p1 < /autoware/patches/llh_converter_plane_20.patch
WORKDIR /autoware

RUN rosdep update \
  && DEBIAN_FRONTEND=noninteractive rosdep install -y --ignore-src --from-paths src --rosdistro "$ROS_DISTRO" \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

## Additional python modules for carlaBridge
# RUN pip3 install simple_pid==1.*

## Clean up unnecessary files
RUN rm -rf \
  "$HOME"/.cache \
  /etc/apt/sources.list.d/cuda*.list \
  /etc/apt/sources.list.d/docker.list \
  /etc/apt/sources.list.d/nvidia-docker.list

## Register Vulkan GPU vendors
RUN curl https://gitlab.com/nvidia/container-images/vulkan/raw/dc389b0445c788901fda1d85be96fd1cb9410164/nvidia_icd.json -o /etc/vulkan/icd.d/nvidia_icd.json \
  && chmod 644 /etc/vulkan/icd.d/nvidia_icd.json
RUN curl https://gitlab.com/nvidia/container-images/opengl/raw/5191cf205d3e4bb1150091f9464499b076104354/glvnd/runtime/10_nvidia.json -o /etc/glvnd/egl_vendor.d/10_nvidia.json \
  && chmod 644 /etc/glvnd/egl_vendor.d/10_nvidia.json

## Register OpenCL GPU vendors
RUN mkdir -p /etc/OpenCL/vendors \
  && echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd \
  && chmod 644 /etc/OpenCL/vendors/nvidia.icd

## Create entrypoint
# hadolint ignore=DL3059
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" > /etc/bash.bashrc
CMD ["/bin/bash"]

## Build and change permission for runtime data conversion
RUN source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && colcon build --parallel-workers 2 --cmake-args -DCMAKE_BUILD_TYPE=Release \
  && find /autoware/install -type d -exec chmod 777 {} \;

COPY carlaBridge /autoware/carlaBridge/
RUN ln -s /autoware/carlaBridge/cppnode /autoware/src/pasta

RUN apt-get update
RUN source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && rosdep update && DEBIAN_FRONTEND=noninteractive rosdep install -y --ignore-src --from-paths src --rosdistro "$ROS_DISTRO"

## Build and change permission for runtime data conversion
RUN source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && source /autoware/install/setup.bash \
  && colcon build --parallel-workers 2 --cmake-args -DCMAKE_BUILD_TYPE=Release --base-path=src \
  && find /autoware/install -type d -exec chmod 777 {} \;

## Copy op_bridge and op_agent into root
WORKDIR /root

## Add Carla ROS2 - Autoware Bridge
RUN ln -s /autoware/carlaBridge carlaBridge
RUN chmod a+x /root/carlaBridge/*.py
RUN chmod a+x /root/carlaBridge/*.sh

## Add Carla Python to root
COPY carlaPython/ /root/carlaPython/

# Copy wsl config
COPY docker/wsl2_image/wsl.conf /etc/wsl.conf

## Create a link of the op_scripts script
RUN ln -sr carlaBridge/run_exploration_mode_ros2.sh run_exploration_mode_ros2.sh

RUN ln -s /autoware/install/attack_lidar_blind/share/attack_lidar_blind/scripts/lidar_attack_control.sh lidar_attack_control.sh
RUN chmod a+x lidar_attack_control.sh

RUN ln -s /autoware/install/attack_gnss/share/attack_gnss/scripts/gnss_attack_control.sh gnss_attack_control.sh
RUN chmod a+x gnss_attack_control.sh

RUN ln -s /autoware/install/attack_ethernet/share/attack_ethernet/scripts/ethernet_attack_control.sh ethernet_attack_control.sh
RUN chmod a+x ethernet_attack_control.sh

## Required for WSL2 vGPU 3D accel
RUN echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/wsl/lib" >> /etc/bash.bashrc

## Create entrypoint
RUN echo "source /autoware/install/setup.bash" >> /etc/bash.bashrc
RUN echo "export CYCLONEDDS_URI='file:///autoware/cyclonedds.xml'" >> /etc/bash.bashrc
CMD ["/bin/bash"]

# hadolint ignore=DL3006
FROM $PREBUILT_BASE_IMAGE as prebuilt

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG ROS_DISTRO
ARG SETUP_ARGS

## Fix broken Ubuntu 22.04 Mesa for WSL2 Docker https://bugs.launchpad.net/ubuntu/+source/mesa/+bug/2004649
## TODO: remove/re-evaluate after Ubuntu 24.04 is released
## Fix OpenGL issues (e.g. black screen in rviz2) due to old mesa lib in Ubuntu 22.04
## See https://github.com/autowarefoundation/autoware.universe/issues/2789
# hadolint ignore=DL3008
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y software-properties-common \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y gpg-agent dirmngr gpg \
  && apt-add-repository ppa:kisak/kisak-mesa \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
  libegl-mesa0 libegl1-mesa-dev libgbm-dev libgbm1 libgl1-mesa-dev libgl1-mesa-dri libglapi-mesa libglx-mesa0

# add boost
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
  python3-numpy \
  libboost-python-dev \
  libboost-numpy-dev 

# TODO massive problem how do I solve this propeyly:
#      I want to link .sos from above but they look like: /usr/lib/x86_64-linux-gnu/libboost_numpy310.so
#      (so to build against it would need -lboost_numpy310 -lboost_python310 and -lpython3.10) so I need to lock in
#      a version here or generically search for proper version to symlink in the pythonStubGeneration script
RUN ln -s /usr/lib/x86_64-linux-gnu/libboost_numpy310.so /usr/lib/x86_64-linux-gnu/libboost_numpy.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libboost_python310.so /usr/lib/x86_64-linux-gnu/libboost_python3.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libpython3.10.so /usr/lib/x86_64-linux-gnu/libpython.so

## Install apt packages
# hadolint ignore=DL3008
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
  git \
  ssh \
  less \
  nano \
  unzip \
  iputils-ping \
  avahi-daemon \
  bc \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

## Copy files
COPY autoware.repos setup-dev-env.sh ansible-galaxy-requirements.yaml amd64.env arm64.env cyclonedds.xml /autoware/
COPY ansible/ /autoware/ansible/

WORKDIR /autoware
RUN ls /autoware

## Add GitHub to known hosts for private repositories
RUN mkdir -p ~/.ssh \
  && ssh-keyscan github.com >> ~/.ssh/known_hosts \
  && ssh-keyscan -p 8022 gitlab.fixstars.com >> ~/.ssh/known_hosts

## Set up runtime environment
RUN --mount=type=ssh \
  ./setup-dev-env.sh -y $SETUP_ARGS --no-cuda-drivers --runtime universe \
  && pip uninstall -y ansible ansible-core \
  && mkdir src \
  && vcs import src < autoware.repos

# Patch introduced humble autoware namespace collision https://github.com/autowarefoundation/autoware.universe/pull/5089
RUN mkdir -p /autoware/patches
COPY patches/autoware_auto_tf2_humble_fix_5089.patch /autoware/patches/
COPY patches/autoware_map_loader_visualize_crosswalk_ids.patch /autoware/patches/
COPY patches/autoware_goal_planner_fix_4472.patch /autoware/patches/
COPY patches/autoware_mission_planner_routing_api_4942.patch /autoware/patches/
COPY patches/autoware_mpc_fix_4673.patch /autoware/patches/
COPY patches/llh_converter_plane_20.patch /autoware/patches/
WORKDIR /autoware/src/universe/autoware.universe
RUN patch -p1 < /autoware/patches/autoware_auto_tf2_humble_fix_5089.patch
RUN patch -p1 < /autoware/patches/autoware_map_loader_visualize_crosswalk_ids.patch
RUN patch -p1 < /autoware/patches/autoware_goal_planner_fix_4472.patch
RUN patch -p1 < /autoware/patches/autoware_mission_planner_routing_api_4942.patch
RUN patch -p1 < /autoware/patches/autoware_mpc_fix_4673.patch
WORKDIR /autoware/src/universe/external/llh_converter
RUN patch -p1 < /autoware/patches/llh_converter_plane_20.patch
WORKDIR /autoware

RUN rosdep update && DEBIAN_FRONTEND=noninteractive rosdep install -y --ignore-src --from-paths src --rosdistro "$ROS_DISTRO"

## Register Vulkan GPU vendors
ADD "https://gitlab.com/nvidia/container-images/vulkan/raw/dc389b0445c788901fda1d85be96fd1cb9410164/nvidia_icd.json" /etc/vulkan/icd.d/nvidia_icd.json
RUN chmod 644 /etc/vulkan/icd.d/nvidia_icd.json
ADD "https://gitlab.com/nvidia/container-images/opengl/raw/5191cf205d3e4bb1150091f9464499b076104354/glvnd/runtime/10_nvidia.json" /etc/glvnd/egl_vendor.d/10_nvidia.json
RUN chmod 644 /etc/glvnd/egl_vendor.d/10_nvidia.json

## Python required for op_bridge
RUN pip3 install simple_pid==1.*

## Add Town01 Map as a default map
RUN mkdir -p /root/maps
COPY maps/README.md /root/maps/
COPY maps/Town01 /root/maps/Town01/
COPY maps/Town03 /root/maps/Town03/

## Copy install folder from builder
COPY --from=devel /autoware/install/ /autoware/install/

# TODO Throwing stuff at wall to see what sticks (was stubGeneration script accesible)
COPY --from=devel /autoware/carlaBridge/cppnode/pasta-interface/python /root/apiInterface
COPY --from=devel /autoware/carlaBridge/cppnode/pasta-interface/include/pasta_interface.hpp /root/apiInterface/include/
COPY --from=devel /autoware/carlaBridge/cppnode/pasta-interface/server/startServers.sh /root/
COPY --from=devel /autoware/carlaBridge/cppnode/pasta-interface/server/stopServers.sh /root/
RUN ln -s /autoware/install/pasta-interface/bin /root/apiServers
## Copy op_bridge and op_agent into root
WORKDIR /root

# Install Carla Autoware packages
COPY carlaBridge/cppnode /autoware/src/

RUN rosdep update \
  && DEBIAN_FRONTEND=noninteractive rosdep install -y --ignore-src --from-paths /autoware/src --rosdistro "$ROS_DISTRO" \
  && rm -rf /autoware/src \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

## Clean up unnecessary files
RUN rm -rf \
  "$HOME"/.cache \
  /etc/apt/sources.list.d/cuda*.list \
  /etc/apt/sources.list.d/docker.list \
  /etc/apt/sources.list.d/nvidia-docker.list

## Add Carla ROS2 - Autoware Bridge
COPY carlaBridge/ /root/carlaBridge/ 
RUN chmod a+x /root/carlaBridge/*.py
RUN chmod a+x /root/carlaBridge/*.sh

## Add Carla Python to root
COPY carlaPython/ /root/carlaPython/

# Copy wsl config
COPY docker/wsl2_image/wsl.conf /etc/wsl.conf

## Create a link of the op_scripts script
RUN ln -sr carlaBridge/run_exploration_mode_ros2.sh run_exploration_mode_ros2.sh

RUN ln -s /autoware/install/attack_lidar_blind/share/attack_lidar_blind/scripts/lidar_attack_control.sh lidar_attack_control.sh
RUN chmod a+x lidar_attack_control.sh

RUN ln -s /autoware/install/attack_gnss/share/attack_gnss/scripts/gnss_attack_control.sh gnss_attack_control.sh
RUN chmod a+x gnss_attack_control.sh

RUN ln -s /autoware/install/attack_ethernet/share/attack_ethernet/scripts/ethernet_attack_control.sh ethernet_attack_control.sh
RUN chmod a+x ethernet_attack_control.sh

## Required for WSL2 vGPU 3D accel
RUN echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/wsl/lib" >> /etc/bash.bashrc
## TODO above is in twice is that right?

## Create entrypoint
RUN echo "source /autoware/install/setup.bash" >> /etc/bash.bashrc
RUN echo "export CYCLONEDDS_URI='file:///autoware/cyclonedds.xml'" >> /etc/bash.bashrc
CMD ["/bin/bash"]
