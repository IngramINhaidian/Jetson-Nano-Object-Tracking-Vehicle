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

def video_capture(frame_queue, darknet_image_queue):
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height),
                                   interpolation=cv2.INTER_LINEAR)
        frame_queue.put(frame_resized)
        img_for_detect = darknet.make_image(width, height, 3)
        darknet.copy_image_from_bytes(img_for_detect, frame_resized.tobytes())
        darknet_image_queue.put(img_for_detect)
    cap.release()

def inference(darknet_image_queue, detections_queue, fps_queue):
    while cap.isOpened():
        darknet_image = darknet_image_queue.get()
        prev_time = time.time()
        detections = darknet.detect_image(network, class_names, darknet_image, thresh=darknet_config["thresh"])
        detections_queue.put(detections)
        fps = int(1/(time.time() - prev_time))
        fps_queue.put(fps)
        print("FPS: {}".format(fps))
        darknet.print_detections(detections, True)
        darknet.free_image(darknet_image)
    cap.release()

def ver_hori_measure(detections_queue, order_queue):
    while cap.isOpened():
        dtcts = detections_queue.get()
        for label, confidence, bbox in detections:
            if label == "bottle":
                x, y, w, h = bbox
                error_y = y - 208
                error_x = x - 208
                order = order_queue.get()
                order.error_rl = error_x
                order.error_ud = error_y
                order_queue.put(order)
    cap.release()

def drawing(frame_queue, detections_queue, fps_queue):
    random.seed(3)  # deterministic bbox colors
    video = set_saved_video(cap, "", (width, height))
    while cap.isOpened():
        frame_resized = frame_queue.get()
        detections = detections_queue.get()
        fps = fps_queue.get()
        if frame_resized is not None:
            image = darknet.draw_boxes(detections, frame_resized, class_colors)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if cv2.waitKey(fps) == 27:
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
                            framerate=30/1 ! nvvidconv filp=method=0 ! \
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
    cap = cv2.VideoCapture(input_path)
    Thread(target=video_capture, args=(frame_queue, darknet_image_queue)).start()
    Thread(target=inference, args=(darknet_image_queue, detections_queue, fps_queue)).start()
    Thread(target=drawing, args=(frame_queue, detections_queue, fps_queue)).start()
