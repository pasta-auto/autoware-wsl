#!/bin/bash

WSL_MOUNT_CMD="wsl.exe --mount 'C:\\wslAutowareExport\\pasta_autoware.vhdx' --name autoware_vhdx --vhd"
WSL_UNMOUNT_CMD="wsl.exe --unmount '\\\\?\\C:\\wslAutowareExport\\pasta_autoware.vhdx'"

DOCKER_IMAGE="gitlab.fixstars.com:5005/pasta/autoware:humble-latest-prebuilt-cuda"

trap 'previous_command=$this_command; this_command=$BASH_COMMAND' DEBUG

function trap_cmd_failed()
{
    echo "$(tput bold)Command '${previous_command}' failed!!$(tput sgr0)"
}

function trap_cmd_unmount_failed()
{
    echo "$(tput bold)Command '${previous_command}' failed!!"
    echo "VHDX needs to be unmounted manually with command $(tput smso)${WSL_UNMOUNT_CMD}$(tput sgr0)"
}

# exit on error
set -e

trap trap_cmd_failed ERR

# Get script dir
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Create temp dir on windows drive
if [ ! -e /mnt/c ]
then
    echo "/mnt/c does not appear to exist"
    exit 1
fi

mkdir -p /mnt/c/wslAutowareExport

# Ungzip a blank vhdx file to export into 
gzip -dkc ${SCRIPT_DIR}/blank_ext4.vhdx.gz > /mnt/c/wslAutowareExport/pasta_autoware.vhdx

echo "$(tput bold)Mounting pasta_autoware.vhdx"
eval $WSL_MOUNT_CMD

trap trap_cmd_unmount_failed ERR

# change working dir
cd /mnt/wsl/autoware_vhdx

IMAGEID=$(docker create $DOCKER_IMAGE)

echo "Container ID is $IMAGEID"

echo "$(tput bold)Exporting to vhdx, sudo password may be required$(tput sgr0)"
docker export $IMAGEID | sudo tar xf -

RMIMAGEID=$(docker container rm $IMAGEID)
echo "Removed container ${RMIMAGEID}"

cd $SCRIPT_DIR

# Sleep to allow writes to complete to mount or unmount fails
sync
sleep 5

echo "$(tput bold)Unmounting VHDX$(tput sgr0)"
eval $WSL_UNMOUNT_CMD

trap trap_cmd_failed ERR

echo "$(tput bold)Moving vxdx to ${SCRIPT_DIR}$(tput sgr0)"
mv /mnt/c/wslAutowareExport/pasta_autoware.vhdx $SCRIPT_DIR/
rmdir /mnt/c/wslAutowareExport

echo -e "$(tput bold)Zipping may take 5-10 min, does not show progress when it is working$(tput sgr0)"
zip pasta_autoware_wsl2.zip pasta_autoware.vhdx
rm pasta_autoware.vhdx


