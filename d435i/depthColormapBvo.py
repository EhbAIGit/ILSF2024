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

def detectCircle(color_image):
    #cimg = cv2.cvtColor(color_image,cv2.COLOR_GRAY2BGR)
    img = cv2.medianBlur(cv2.cvtColor(color_image,cv2.COLOR_BGR2GRAY) , 5)
    circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1.5,20, param1=50,param2=30,minRadius=23,maxRadius=30)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # # draw the outer circle
            x, y, radius = i
            cv2.circle(color_image,(x,y),radius,(0,0,255),3)
            print(x, y, radius)


def main():
    dc = DepthCamera()
    
    while True:
        # Get depth frame
        depth_frame = dc.get_frame()

        # Convert depth frame to numpy array
        depth_image = np.asanyarray(depth_frame.get_data())

        # Crop the center of the image with a size of 500x500 pixels
        cropped_depth_image = depth_image#[40:540, 70:570]
        

        # Clip depth values between 20 cm and 1 meter
        clipped_depth_image = np.clip(cropped_depth_image, 200, 650)  # Depth values are in millimeters

        # Create a copy of the clipped depth image for visualization
        depth_visualized = cv2.cvtColor(clipped_depth_image.astype(np.uint8), cv2.COLOR_GRAY2BGR)

        # Make points with distance greater than 30 cm black
        depth_visualized[clipped_depth_image > 1000] = [0, 0, 0]
        #depth_visualized[clipped_depth_image < 400] = [255, 255, 255]
        
        #depth_visualized[np.logical_not(np.logical_and(clipped_depth_image >= 400, clipped_depth_image <= 490)) ]  = [255, 255, 255]

        #depth_visualized[np.logical_and(clipped_depth_image >= 400, clipped_depth_image <= 490) ]  = [0, 255, 255]

        
        detectCircle(depth_visualized)
        print("-----")

        # Draw a rectangle around the cropped area
        #cv2.rectangle(depth_visualized, (0, 0), (500, 500), (255, 255, 255), 2)

        # Display the depth colormap
        cv2.imshow('Depth Colormap', depth_visualized)
        
        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
