import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import os
from PIL import Image as PILImage
from io import BytesIO

from ultralytics import YOLO

# load the model
model = YOLO("yolov8n.pt")


class IntelSubscriber(Node):
    def __init__(self):
        super().__init__("intel_subscriber")
        self.subscription_rgb = self.create_subscription(Image,"rgb_frame",self.rgb_frame_callback,10)
        self.br_rgb = CvBridge()
        # self.image_directory = '/ObjectTrackingUsingEyeGaze/YOLO-Object-Detection/darknet/data'
        self.timer = self.create_timer(10,self.timerCallback)
        # self.image_captured = False

    def rgb_frame_callback(self, data):
        self.get_logger().warning("Receiving RGB frame")
        
        try:
            # Check the encoding of the incoming image
            if data.encoding == "bgr8" or data.encoding == "rgb8":
                current_frame = self.br_rgb.imgmsg_to_cv2(data, "bgr8")
            elif data.encoding == "8UC3":
                current_frame = self.br_rgb.imgmsg_to_cv2(data)
            else:
                self.get_logger().error(f"Unsupported encoding: {data.encoding}")
                return

        except CvBridgeError as e:
            self.get_logger().error(f"Failed to convert image: {str(e)}")
            return
        rgb_frame = cv2.cvtColor(current_frame,cv2.COLOR_BGR2RGB)
        pil_img = PILImage.fromarray(rgb_frame)

        # run inference
        results = model([pil_img])
        

        # object detection
        # results = model(current_frame,stream=True)
        for i,result in enumerate (results):
            im_bgr = result.plot()
            im_rgb = PILImage.fromarray(im_bgr[...,::-1])
            result.show()
            annotated_frame = cv2.cvtColor(im_bgr,cv2.COLOR_RGB2BGR)

            cv2.imshow("Detected objects", annotated_frame)
            cv2.waitKey(1)

        self.destroy_timer(self.timer)
        cv2.waitKey(1)


    def timerCallback(self):
        self.get_logger().info("10 seconds passed, capturing an image.")

    # def detection_callback(self,current_frame):
    #     # run inference on the source
    #     results = model(source=current_frame,conf=0.4,save=True)
    #     return results

# you need to write a class to send images to yolo directly
# see what yolo outputs

# class YOLO_detection():

#     def __init__(self):
#         self.get_logger().info

def main():
    rclpy.init()
    intel_subscriber = IntelSubscriber()
    rclpy.spin(intel_subscriber)
    intel_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()