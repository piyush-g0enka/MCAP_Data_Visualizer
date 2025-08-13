## MCAP Data Visualizer - RESIM TECHNICAL CHALLENGE

### INTRODUCTION

The application reads an MCAP file containing odometry and tracked object data, then 
visualizes the robot's movement and nearby obstacles using an animated Matplotlib 
plot. It dynamically updates the robot's position, detects the nearest object, and displays 
the distance between them. 

### STEPS TO RUN THE DOCKER CONTAINER (Ubuntu)

First create a docker container with the given DockerFile and source files. Then download the mcap-visualizer.tar file in a folder. 
Then follow the below steps to run the container 

#### use sudo if there are permission issues 

#### Load the image 
$ docker load -i mcap-visualizer.tar 

#### Verify the image. Check if the image name shows up in the list 
$ docker images 

#### Allow docker to access host XServer to display the visualization.  
$ xhost +local:docker 

#### Run the docker container 
$ docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix 
mcap-visualizer 
