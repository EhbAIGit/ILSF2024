import cv2
import pyrealsense2 as rs
import numpy as np
from numpy import ndarray

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

class CenterSlicer:
    def __init__(self, twodarray:ndarray):
        self.twodarray = twodarray
        self.height, self.width = twodarray.shape
        self.xCenter = int(self.height / 2)
        self.yCenter = int(self.width / 2)

    def sliceFromCenter(self, distance):
        return CenterSlicer(self.twodarray[(self.xCenter - distance):(self.xCenter + distance),
                                  (self.yCenter - distance):(self.yCenter + distance)])

        
    def sliceFromCenterWithBoundaries(self, xBefore=0, xAfter=0, yBefore=0, yAfter=0):
        return CenterSlicer(self.twodarray[(self.xCenter - xBefore):(self.xCenter + xAfter),
                                  (self.yCenter - yBefore):(self.yCenter + yAfter)])
        
    def getArray(self):
        return self.twodarray
    
    def getCenterValue(self):
        return self.twodarray[self.xCenter, self.yCenter]
    
    def check(self):
        a = 425.0
        b = 3
        return np.all((self.twodarray >= a - b) & (self.twodarray <= a + b))
        
        
    def stdDevation(self):
        return np.std(self.twodarray)
    
    def __str__(self):
        result = ''
        for a in self.twodarray:
            for b in a:
                result += "{:.3f} ".format(b)
            result += "\n"
        return result
    
def detectCircle(color_image):
    #cimg = cv2.cvtColor(color_image,cv2.COLOR_GRAY2BGR)
    img = cv2.medianBlur(cv2.cvtColor(color_image,cv2.COLOR_BGR2GRAY) , 5)
    circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20, param1=50,param2=30,minRadius=20,maxRadius=100)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # # draw the outer circle
            x, y, radius = i
            #cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
            # # draw the center of the circle
            # cv2.circle(color_image,(i[0],i[1]),2,(0,0,255),3)
            print(x, y, radius)

def main():
    dc = DepthCamera()
    
    while True:
        # Get frames
        depth_frame, color_frame = dc.get_frame()

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        print("-----------------------------")
        print(CenterSlicer(depth_image).sliceFromCenter(3).check())
        print("-----------------------------")

        # Get width and height of the depth frame
        height, width = depth_image.shape
        center = (int(width / 2), int(height / 2))

        # Get the depth value at the center of the depth frame
        depth_center = depth_image[int(height / 2), int(width / 2)]

        # Convert depth value to meters
        distance = depth_center / 10  # Convert mm to meters


        # Draw a red crosshair at the center of the screen
        cv2.line(color_image, (int(width / 2) - 20, int(height / 2)), (int(width / 2) + 20, int(height / 2)), (0, 0, 255), 2)
        cv2.line(color_image, (int(width / 2), int(height / 2) - 20), (int(width / 2), int(height / 2) + 20), (0, 0, 255), 2)
        cv2.circle(color_image, center, 55, (0, 0, 255), 2)

        # Display the color frame with the distance on the screen
        cv2.putText(color_image, f"Distance: {distance:.2f} cm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Color Frame', color_image)
        
        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
