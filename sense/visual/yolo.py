from ctypes import *
import random
import os
import cv2
import time
from . import darknet
import argparse
from threading import Thread, enumerate
from queue import Queue

def set_saved_video(input_video, output_video, size):
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    fps = int(input_video.get(cv2.CAP_PROP_FPS))
    video = cv2.VideoWriter(output_video, fourcc, fps, size)
    return video

# put to frame_queue
# put to darknet_image_queue
def video_capture(cap, frame_queue, darknet_image_queue):
    width=1280
    height = 780
    while cap.isOpened():
        ret, frame = cap.read()
        #if not ret:
        #    break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height),
                                   interpolation=cv2.INTER_LINEAR)
        print("Stuck useless z")
        if frame_queue.full():
            z = frame_queue.get()
        print("Stuck frame_queue & video_capture")
        frame_queue.put(frame_resized)
        img_for_detect = darknet.make_image(width, height, 3)
        darknet.copy_image_from_bytes(img_for_detect, frame_resized.tobytes())
        trash = frame_queue.get()
        print("Stuck useless y")
        if darknet_image_queue.full():
            y = darknet_image_queue.get()
        print("Stuck darknet_img_queue & video capture")
        darknet_image_queue.put(img_for_detect)
    cap.release()


# get from darknet_image_queue
# put to detections_queue
# abandon fps_queue
def inference(pack, cap, darknet_image_queue, detections_queue, fps_queue):
    while cap.isOpened():
        if not darknet_image_queue.empty():
            darknet_image = darknet_image_queue.get()
            prev_time = time.time()
            detections = darknet.detect_image(pack[0], pack[1], darknet_image, thresh=.25)
            # detections = darknet.detect_image(network, class_names, darknet_image, thresh=darknet_config["thresh"])
            
            print("Stck useless x")
            if detections_queue.full():
                x = detections_queue.get()
            print("Stuck detections_queue & inference")
            detections_queue.put(detections)
            print("fuck")
            fps = int(1/(time.time() - prev_time))
            # fps_queue.put(fps)
            print("FPS: {}".format(fps))
            darknet.print_detections(detections, True)
            darknet.free_image(darknet_image)
        else:
            print("darknet_image_queue is always empty!")
    cap.release()

# get from detections_queue
# get from pre_order_queue
# put to order_queue
def ver_hori_measure(cap, detections_queue, pre_order_queue, order_queue):
    while True:
        if not detections_queue.empty():
            detections = detections_queue.get()
            for label, confidence, bbox in detections:
                if label == "bottle":
                    x, y, w, h = bbox
                    error_y = y - 208
                    error_x = x - 208
                    if not pre_order_queue.empty():
                        order = pre_order_queue.get()
                        order.error_rl = error_x
                        order.error_ud = error_y
                        print("Stuck order_queue & ver_hori_measure")
                        order_queue.put(order)
                    else:
                        print("pre_order_queue is always empty!")
                # 让pre_order_queue能及时清空
                else:
                    if not pre_order_queue.empty():
                        trash = pre_order_queue.get()
                # 避免一瞬间detections获得多个bottle的情况
                break
        else:
            print("detections_queue is always empty!")
    cap.release()

def drawing(cap, frame_queue, detections_queue, fps_queue):
    random.seed(3)  # deterministic bbox colors
    video = set_saved_video(cap, "", (width, height))
    while cap.isOpened():
        frame_resized = frame_queue.get()
        detections = detections_queue.get()
        fps = fps_queue.get()
        if frame_resized is not None:
            image = darknet.draw_boxes(detections, frame_resized, class_colors)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if cv2.waitKey() == 27:
                break
    cap.release()
    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    frame_queue = Queue()
    darknet_image_queue = Queue(maxsize=1)
    detections_queue = Queue(maxsize=1)
    fps_queue = Queue(maxsize=1)

    darknet_config = {
        "input" : "nvarguscamerasrc ! video/x-raw(memory:NVMM),\
                            width=1280, height=720, format=NV12, \
                            framerate=30/1 ! nvvidconv filp-method=0 ! \
                            video/x-raw, width=1280, height=720, format=BGRx ! \
                            videoconvert ! video/x-raw, format=BGR ! appsink",
        "config_file" : "yolov4-tiny.cfg",
        "data_file"   : "coco.data",
        "weights"     : "yolov4-tiny.weights",
        "thresh"      : .25
    }


    network, class_names, class_colors = darknet.load_network(
            darknet_config["config_file"],
            darknet_config["data_file"],
            darknet_config["weights"],
            batch_size=1
        )
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    input_path = darknet_config["input"]
    #cap = cv2.VideoCapture(input_path)
    cap = cv2.VideoCapture(0)
    Thread(target=video_capture, args=(frame_queue, darknet_image_queue)).start()
    Thread(target=inference, args=(darknet_image_queue, detections_queue, fps_queue)).start()
    Thread(target=drawing, args=(frame_queue, detections_queue, fps_queue)).start()
