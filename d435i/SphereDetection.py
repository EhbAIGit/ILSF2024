import cv2
import pyrealsense2 as rs
import numpy as np
from numpy import ndarray
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

class TwoDimensionArea:
    def __init__(self, twodarray:ndarray):
        self.twodarray = twodarray
        self.height, self.width = twodarray.shape
        self.xCenter = int(self.height / 2)
        self.yCenter = int(self.width / 2)
        
    def sliceFromPosition(self, distance, pos):
        x, y = pos
        return TwoDimensionArea(self.twodarray[(x - distance):(x + distance),
                                  (y - distance):(y + distance)])

    def sliceFromCenterDeviation(self, distance, deviation):
        x, y = deviation
        return self.sliceFromPosition(distance, (self.xCenter + x, self.yCenter + y))

    def sliceFromCenter(self, distance):
        return self.sliceFromPosition(distance, (self.xCenter, self.yCenter))

    def getArray(self):
        return self.twodarray
    
    def getCenterValue(self):
        return self.twodarray[self.xCenter, self.yCenter]
    
    def check(self, distance, deviation):
        return np.all((self.twodarray >= distance - deviation) & (self.twodarray <= distance + deviation))
        
    def stdDevation(self):
        return np.std(self.twodarray)
    
    def __str__(self):
        result = ''
        for a in self.twodarray:
            for b in a:
                result += "{:.3f} ".format(b)
            result += "\n"
        return result
 
class CircleDetector:
    def __init__(self, minRadius, maxRadius):
        self.minRadius = minRadius
        self.maxRadius = maxRadius
    
    def detectCircle(self, color_image):
        img = cv2.medianBlur(cv2.cvtColor(color_image,cv2.COLOR_BGR2GRAY) , 5)
        circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20, param1=50,param2=30,minRadius=self.minRadius,maxRadius=self.maxRadius)
        return circles

def record_video(video_name="hello", seconds=300, frame_width=640, frame_height=480):
    out_mp4 = cv2.VideoWriter(f"{video_name}.mp4", cv2.VideoWriter_fourcc(*"XVID"), 10, (frame_width, frame_height))
    dc = DepthCamera()
    
    program_starts = time.time()
    program_ends = program_starts + seconds
    
    while time.time() < program_ends:
        # Get frames
        _, color_frame = dc.get_frame()
        color_image = np.asanyarray(color_frame.get_data())
        out_mp4.write(color_image)
       
    out_mp4.release()
        
def show_distance_in_center():
    dc = DepthCamera()
    
    while True:
        # Get frames
        depth_frame, color_frame = dc.get_frame()

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        print("-----------------------------")
        area = TwoDimensionArea(depth_image).sliceFromCenter(3)
        #print(area)
        print(area.check(200.0, 10))
        circles = CircleDetector(50,100).detectCircle(color_image)
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                # draw the outer circle
                x, y, radius = i
                cv2.circle(color_image,(x,y),radius,(0,255,0),2)
                # draw the center of the circle
                cv2.circle(color_image,(x, y),2,(0,0,255),3)
                print(x, y, radius)
        
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
    
def test_depth():
    depth_image:ndarray = np.loadtxt('depth2d.csv', delimiter=',', dtype=float)
    depth_image_meters = depth_image # Convert mm to meters

    s = TwoDimensionArea(depth_image_meters).sliceFromCenter(3)

    print(s)
    print(s.check(421, 3))
    print(s.stdDevation())
    
def test_circles():
    cimg = cv2.imread('d.jpeg')
    circles = CircleDetector(62, 70).detectCircle(cimg)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            x, y, radius = i
            cv2.circle(cimg,(x,y),radius,(0,255,0),2)
            # draw the center of the circle
            cv2.circle(cimg,(x, y),2,(0,0,255),3)
            print(x, y, radius)
    
    cv2.imshow('detected circles', cimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    menu = [
        ("Test depth", test_depth),
        ("Test circle", test_circles),
        ("Record video", record_video),
        ("Main", show_distance_in_center)
    ]
    
    for (number, (question, function)) in enumerate(menu):
        print(f"{number + 1}. {question}")
    
    number = int(input("Geef je keuze als nummer aub: "))
    
    (question, function) = menu[number-1]
    print(f"Running {question}")
    function()