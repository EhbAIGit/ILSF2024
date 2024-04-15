import cv2
import pyrealsense2 as rs
import numpy as np

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
    
    while True:
        # Get frames
        depth_frame, color_frame = dc.get_frame()

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Get width and height of the depth frame
        height, width = depth_image.shape

        # Get the depth value at the center of the depth frame
        depth_center = depth_image[int(height / 2), int(width / 2)]

        # Convert depth value to meters
        distance = depth_center / 10  # Convert mm to meters


        # Draw a red crosshair at the center of the screen
        cv2.line(color_image, (int(width / 2) - 20, int(height / 2)), (int(width / 2) + 20, int(height / 2)), (0, 0, 255), 2)
        cv2.line(color_image, (int(width / 2), int(height / 2) - 20), (int(width / 2), int(height / 2) + 20), (0, 0, 255), 2)

        # Display the color frame with the distance on the screen
        cv2.putText(color_image, f"Distance: {distance:.2f} cm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Color Frame', color_image)
        
        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
