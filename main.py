#!/usr/bin/env python3

# File name: main.py
# Author: Piyush Goenka
# Description: This file contains a class MCAPVisualizer which reads an MCAP file and 
#               visualizes it's data along with relevant insights
#
# Code structure: MCAPVisualizer
#                       parse_map()
#                       update_animation()
#                       find_nearest_object()
#                       initialize_animation()
#                       animate()

###################################################################################

# Dependencies
import numpy as np
import matplotlib.pyplot as plt
import json
from mcap.reader import make_reader
import matplotlib.patches as patches
import matplotlib.animation as animation

###################################################################################

class MCAPVisualizer:

    def __init__(self, file_path="recording.mcap"):

        # MCAP data attributes
        self.odometry = []
        self.tracked_objects = []
        self.robot_extents = None
        self.timestamps = []
        self.file_path = file_path

        # Visualization attributes
        self.robot_patch = None
        self.obstacle_patch = []
        self.line = None
        self.distance_text = None

    ###############################################################################

    ### Extracts data from MCAP file ###

    def parse_mcap(self):

        with open(self.file_path, "rb") as f:
            reader = make_reader(f)

            for schema, channel, message in reader.iter_messages():

                # Convert binary JSON data
                data = json.loads(message.data.decode())

                # extract odometry data
                if channel.topic == "odometry":
                    self.odometry.append(
                        [data["x"], data["y"], data["theta"]])
                    self.timestamps.append(
                        round(message.publish_time*10e-6, 3))

                # extract objects data
                elif channel.topic == "tracked_objects":

                    obstacle = []
                    for obj in data["objects"]:
                        obstacle.append({"pose": [obj["pose"]["x"], obj["pose"]["y"], obj["pose"]["theta"]],
                                         "extents": (obj["extents"]["x"], obj["extents"]["y"])
                                         }
                                        )

                    self.tracked_objects.append(obstacle)

                # extract robot extents
                elif channel.topic == "robot_extents":
                    self.robot_extents = [data["x"], data["y"]]

    ###############################################################################

    ### Updates the animation for each frame ###

    def update_animation(self, frame, ax):

        # initialize the animation objects 
        if frame == 0:
            self.initialize_animation(ax)

        # update robot patch
        robot_x, robot_y, robot_theta = self.odometry[frame]
        robot_extent_x, robot_extent_y = self.robot_extents
        self.robot.set_xy((robot_x - robot_extent_x/2,
                          robot_y - robot_extent_y/2))
        self.robot.set_angle(robot_theta*180/3.14)
        ax.scatter(robot_x, robot_y, color='b', marker='.')

        # update object patches
        object_positions = []

        for obj, obj_patch in zip(self.tracked_objects[frame], self.objects):
            obj_x, obj_y, obj_theta = obj["pose"]
            obj_extent_x, obj_extent_y = obj["extents"]

            object_positions.append([obj_x, obj_y])

            obj_patch.set_xy((obj_x - obj_extent_x/2, obj_y - obj_extent_y/2))
            obj_patch.set_angle(obj_theta*180/3.14)
            obj_patch.set_width(obj_extent_x)
            obj_patch.set_height(obj_extent_y)

        # compute nearest object and draw a line between the object and robot
        nearest_obj_x, nearest_obj_y = self.find_nearest_object(
            robot_x, robot_y, object_positions)
        self.line.set_data([robot_x, nearest_obj_x], [robot_y, nearest_obj_y])

        # Compute and update the distance between robot and nearest object
        distance = np.sqrt((robot_x - nearest_obj_x)**2 +
                           (robot_y - nearest_obj_y)**2)
        mid_x, mid_y = (nearest_obj_x + robot_x) / \
            2, (nearest_obj_y + robot_y) / 2
        self.distance_text.set_position((mid_x, mid_y))
        self.distance_text.set_text(f'{distance:.2f}')
    
    ###############################################################################

    ### Computes xy position of nearest object to robot###

    def find_nearest_object(self, x, y, points):
        return min(points, key=lambda p: np.sqrt((p[0] - x) ** 2 + (p[1] - y) ** 2))
    
    ###############################################################################

    ### Initializes the animation patches and other art objects ###

    def initialize_animation(self, ax):

        ax.clear()
        ax.set_xlim(-6, 6)
        ax.set_ylim(-6, 6)
        ax.set_xlabel("X Position (m)")
        ax.set_ylabel("Y Position (m)")
        ax.set_title("MCAP Visualization (unit:Meter)")
        ax.scatter([], [], color='blue', marker='s', label='Robot')
        ax.scatter([], [], color='red', marker='s', label='Obstacle')
        ax.legend()
        ax.set_aspect('equal')

        self.line, = ax.plot([], [], 'g', linewidth=1)
        self.distance_text = ax.text(
            0, 0, '', fontsize=8, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.6))

        # initialize robot patch
        self.robot = patches.Rectangle(xy=(0, 0),
                                       width=self.robot_extents[0], height=self.robot_extents[1],
                                       angle=0,
                                       rotation_point='center',
                                       color='blue')

        ax.add_patch(self.robot)

        # initialize object patches
        self.objects = []
        for object in range(0, len(self.tracked_objects)):

            obj_patch = patches.Rectangle(xy=(0, 0),
                                          width=0.0, height=0.0,
                                          angle=0,
                                          rotation_point='center',
                                          color='red')

            self.objects.append(obj_patch)
            ax.add_patch(obj_patch)
   
    ###############################################################################

    ### Animates/Visualizes the MCAP data along with insights ###

    def animate(self):
        fig, ax = plt.subplots(figsize=(16, 16))
        ani = animation.FuncAnimation(
            fig, self.update_animation, frames=len(self.timestamps), fargs=(ax,),
            interval=self.timestamps[1]-self.timestamps[0], blit=False
        )

        plt.show()

###################################################################################


if __name__ == "__main__":

    file_path = 'recording.mcap'
    vi = MCAPVisualizer(file_path)
    vi.parse_mcap()
    vi.animate()
