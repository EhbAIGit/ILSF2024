import cv2
import pyrealsense2 as rs
import numpy as np
import time

class DepthCamera:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(self.config)

    def __del__(self):
        self.pipeline.stop()

    def get_frame(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        return depth_frame, color_frame

def main():
    dc = DepthCamera()
    time.sleep(3)

    # Get frames
    depth_frame, color_frame = dc.get_frame()

    # Convert images to numpy arrays
    depth_image = np.asanyarray(depth_frame.get_data())
    # color_image = np.asanyarray(color_frame.get_data())

    # Get width and height of the depth frame
    height, width = depth_image.shape

    # Get the depth value at the center of the depth frame
    depth_center = depth_image[int(height / 2), int(width / 2)]

    # Convert depth value to meters
    distance = depth_center / 10  # Convert mm to meters
    print(f"Height = {height}, width = {width} Middle distance is {distance}")
    #print(depth_image)

    for i in range(height):
        for j in range(width):
            print(f"{depth_image[i,j]},", end="")
        print()



if __name__ == "__main__":
    main()
