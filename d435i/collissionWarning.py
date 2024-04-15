import cv2
import numpy as np
import pyrealsense2 as rs

class DepthCamera:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.pipeline.start(self.config)

    def __del__(self):
        self.pipeline.stop()

    def get_frame(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        return depth_frame

def main():
    dc = DepthCamera()
    
    while True:
        # Get depth frame
        depth_frame = dc.get_frame()

        # Convert depth frame to numpy array
        depth_image = np.asanyarray(depth_frame.get_data())

        # Convert depth values to meters
        depth_image_meters = depth_image * 0.001  # Convert mm to meters

        # Find indices where distance is less than 25 cm
        collision_indices = np.where(depth_image_meters < 0.25)

        # Create an empty color image
        color_image = np.zeros((480, 640, 3), dtype=np.uint8)

        # Draw a red rectangle around the potential collision area
        if len(collision_indices[0]) > 0:
            min_x = np.min(collision_indices[1])
            max_x = np.max(collision_indices[1])
            min_y = np.min(collision_indices[0])
            max_y = np.max(collision_indices[0])
            cv2.rectangle(color_image, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)

        # Display the color image with collision warning
        cv2.imshow('Collision Warning', color_image)

        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
