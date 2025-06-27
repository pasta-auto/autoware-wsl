# Autoware WSL image

![Autoware_RViz](https://user-images.githubusercontent.com/63835446/158918717-58d6deaf-93fb-47f9-891d-e242b02cba7b.png)
[![Discord](https://img.shields.io/discord/953808765935816715?label=Autoware%20Discord&style=for-the-badge)](https://discord.gg/Q94UsPvReQ)

Autoware is an open-source software stack for self-driving vehicles, built on the [Robot Operating System (ROS)](https://www.ros.org/). It includes all of the necessary functions to drive an autonomous vehicles from localization and object detection to route planning and control, and was created with the aim of enabling as many individuals and organizations as possible to contribute to open innovations in autonomous driving technology.

![Autoware architecture](https://static.wixstatic.com/media/984e93_552e338be28543c7949717053cc3f11f~mv2.png/v1/crop/x_0,y_1,w_1500,h_879/fill/w_863,h_506,al_c,usm_0.66_1.00_0.01,enc_auto/Autoware-GFX_edited.png)

## Getting the Source
```
git clone ssh://github.com/pasta-auto/autoware
```
## Building Requirements
- WSL2 setup on your system with Ubuntu installed
   - This can be done by running `wsl --install Ubuntu` on the system
      - Windows may need to reboot after running this command before Ubuntu is properly installed. If an error appears after downloading Ubuntu reboot the machine and try running the command again
   - Ensure `zip` is installed within the Ubuntu WLS2
      - This can be done with `sudo apt-get install zip` from the Ubuntu WSL2 shell
- Minimum 32GB of ram with ~24GB allocated to WSL2
   - By default WSL2 is configured for 50% of the machine installed RAM
   - This can be manually changed within the `WSL Settings` application
- ~150GB free space on the harddrive after install Ubuntu
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) needs to be installed on the system and setup to with Ubuntu integration
  - Docker installed within Ubuntu WSL2 should also work but is not fullly tested
## Building
1. Prep the `maps` folder in the source
   1. Create the folders `Town01` and `Town03` in the `maps` folder
   1. Download the maps files
      1. Download [`Town1.pcd`](https://bitbucket.org/carla-simulator/autoware-contents/src/master/maps/point_cloud_maps/Town01.pcd) and rename it to `pointcloud_map.pcd` then place it into the `maps/Town01` folder
      1. Download [`Town3.pcd`](https://bitbucket.org/carla-simulator/autoware-contents/src/master/maps/point_cloud_maps/Town03.pcd) and rename it to `pointcloud_map.pcd` then place it into the `maps/Town03` folder
      1. Download [`Town01.osm`](https://bitbucket.org/carla-simulator/autoware-contents/src/master/maps/vector_maps/lanelet2/Town01.osm) and rename it to `lanelet2_map.osm` then place it into the `maps/Town01` folder
      1. Download [`Town03.osm`](https://bitbucket.org/carla-simulator/autoware-contents/src/master/maps/vector_maps/lanelet2/Town03.osm) and rename it to `lanelet2_map.osm` then place it into the `maps/Town03` folder
1. Run the script `docker/build.sh`
   - This will start the build process. The process takes quite. Depending on the system this build can take anywhere from 1 - 3 hours
   - While build you may notice a folder `c:/wslAutowareExport`. This is expected and part of the build process. The folder should be automatically removed when the build is done.
1. When complete the script will output the pasta_autoware_wsl2.zip to the `docker` directory as an output.

## Documentation

To learn more about using or developing Autoware, refer to the [Autoware documentation site](https://autowarefoundation.github.io/autoware-documentation/main/). You can find the source for the documentation in [autowarefoundation/autoware-documentation](https://github.com/autowarefoundation/autoware-documentation).

## Repository overview

- [autowarefoundation/autoware](https://github.com/autowarefoundation/autoware)
  - Meta-repository containing `.repos` files to construct an Autoware workspace.
  - It is anticipated that this repository will be frequently forked by users, and so it contains minimal information to avoid unnecessary differences.
- [autowarefoundation/autoware_common](https://github.com/autowarefoundation/autoware_common)
  - Library/utility type repository containing commonly referenced ROS packages.
  - These packages were moved to a separate repository in order to reduce CI execution time
- [autowarefoundation/autoware.core](https://github.com/autowarefoundation/autoware.core)
  - Main repository for high-quality, stable ROS packages for Autonomous Driving.
  - Based on [Autoware.Auto](https://gitlab.com/autowarefoundation/autoware.auto/AutowareAuto) and [Autoware.Universe](https://github.com/autowarefoundation/autoware.universe).
- [autowarefoundation/autoware.universe](https://github.com/autowarefoundation/autoware.universe)
  - Repository for experimental, cutting-edge ROS packages for Autonomous Driving.
  - Autoware Universe was created to make it easier for researchers and developers to extend the functionality of Autoware Core
- [autowarefoundation/autoware_launch](https://github.com/autowarefoundation/autoware_launch)
  - Launch configuration repository containing node configurations and their parameters.
- [autowarefoundation/autoware-github-actions](https://github.com/autowarefoundation/autoware-github-actions)
  - Contains [reusable GitHub Actions workflows](https://docs.github.com/ja/actions/learn-github-actions/reusing-workflows) used by multiple repositories for CI.
  - Utilizes the [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) concept.
- [autowarefoundation/autoware-documentation](https://github.com/autowarefoundation/autoware-documentation)
  - Documentation repository for Autoware users and developers.
  - Since Autoware Core/Universe has multiple repositories, a central documentation repository is important to make information accessible from a single place.

## Using Autoware.AI

If you wish to use Autoware.AI, the previous version of Autoware based on ROS 1, switch to [autoware-ai](https://github.com/autowarefoundation/autoware_ai) repository. However, be aware that Autoware.AI has reached the end-of-life as of 2022, and we strongly recommend transitioning to Autoware Core/Universe for future use.

## Contributing

- [There is no formal process to become a contributor](https://github.com/autowarefoundation/autoware-projects/wiki#contributors) - you can comment on any [existing issues](https://github.com/autowarefoundation/autoware.universe/issues) or make a pull request on any Autoware repository!
  - Make sure to follow the [Contribution Guidelines](https://autowarefoundation.github.io/autoware-documentation/main/contributing/).
  - Take a look at Autoware's [various working groups](https://github.com/autowarefoundation/autoware-projects/wiki#working-group-list) to gain an understanding of any work in progress and to see how projects are managed.
- If you have any technical questions, you can start a discussion in the [Q&A category](https://github.com/autowarefoundation/autoware/discussions/categories/q-a) to request help and confirm if a potential issue is a bug or not.

## Useful resources

- [Autoware Foundation homepage](https://www.autoware.org/)
- [Support guidelines](https://autowarefoundation.github.io/autoware-documentation/main/support/support-guidelines/)
