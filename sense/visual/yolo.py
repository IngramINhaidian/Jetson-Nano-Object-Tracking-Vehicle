from ctypes import *
import random
import os
import cv2
import time
import darknet
import argparse
from threading import Thread, enumerate
from queue import Queue

frame_queue = Queue()
darknet_image_queue = Queue(maxsize=1)
detections_queue = Queue(maxsize=1)
fps_queue = Queue(maxsize=1)

darknet_config = {
    "input" : "nvarguscamerasrc ! video/x-raw(memory:NVMM),\
                        width=1280, height=720, format=NV12, \
                        framerate=30/1 ! nvvidconv filp=method=0 ! \
                        video/x-raw, width=1280, height=720, format=BGRx ! \
                        videoconvert ! video/x-raw, format=BGR ! appsink"
}


network, class_names, class_colors = darknet.load_network(
        args.config_file,
        args.data_file,
        args.weights,
        batch_size=1
    )