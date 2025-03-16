#!/bin/sh

# echo "start program in 45 seconds"

# for i in {0..30}
# do
#   echo $i
#   sleep 1s
# done
# sleep 45
echo "program is starting"
sudo python3 /home/pi/Desktop/Photo_cam/photo_cam.py -c
echo "end of the script"