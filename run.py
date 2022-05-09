from queue import Queue
from control import servoserial
from control import robot_control
from sense.obstacle import distance
from threading import Thread, enumerate, Condition
#from sense import obstacle
from sense import visual
from sense.obstacle import distance
from sense.visual import yolo
import cv2
from sense.visual import darknet


STD_LR = 0  # 左右
STD_UD = 0  # 上下
STD_QH = 0  # 前后

if __name__ == "__main__":
    bot = robot_control.myRobot()
    tof = distance.MyTOF()

    
    frame_queue = Queue()
    darknet_image_queue = Queue(maxsize=1)
    detections_queue = Queue(maxsize=1) # same level
    distance_queue = Queue(maxsize=1) # same level
    order_queue = Queue(maxsize=1)
    pre_order_queue = Queue(maxsize=1)
    fps_queue = Queue(maxsize=1)

    darknet_config = {
        "input" : "nvarguscamerasrc ! video/x-raw(memory:NVMM),width=1280, height=720, format=NV12, framerate=30/1 ! nvvidconv filp=method=0 ! video/x-raw, width=1280, height=720, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink",
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
    # cap = cv2.VideoCapture(input_path)
    cap = cv2.VideoCapture(0)
    # 前后 上下左右线程同步
    cdt = Condition()

    # test
    # bot.begin_dance()

    # start
    Thread(target=yolo.video_capture, args=(cap, frame_queue, darknet_image_queue)).start()
        # frame_queue -> darknet_image_queue
    Thread(target=yolo.inference, args=(cap, darknet_image_queue, detections_queue, fps_queue)).start()
        # darknet_image -> detections_queue
    Thread(target=distance.distance_measure, args=(cap, tof, distance_queue, pre_order_queue)).start()
        # -> distance_queue
    Thread(target=yolo.ver_hori_measure, args=(cap, detections_queue, pre_order_queue, order_queue)).start()
        # detections_qeue -> ver_hori_queue
    Thread(target=robot_control.robot_move, args=(cap, order_queue, bot)).start()
        # 1.distance_queue 2. ver_hori_queue -> order_queue
        # order_queue transform
