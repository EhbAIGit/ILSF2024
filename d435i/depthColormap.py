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

        # Crop the center of the image with a size of 500x500 pixels
        cropped_depth_image = depth_image[40:540, 70:570]

        # Clip depth values between 20 cm and 1 meter
        clipped_depth_image = np.clip(cropped_depth_image, 200, 650)  # Depth values are in millimeters

        # Create a copy of the clipped depth image for visualization
        depth_visualized = cv2.cvtColor(clipped_depth_image.astype(np.uint8), cv2.COLOR_GRAY2BGR)

        # Make points with distance greater than 30 cm black
        depth_visualized[clipped_depth_image > 1000] = [0, 0, 0]


        # Draw a rectangle around the cropped area
        cv2.rectangle(depth_visualized, (0, 0), (500, 500), (255, 255, 255), 2)

        # Display the depth colormap
        cv2.imshow('Depth Colormap', depth_visualized)
        
        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
