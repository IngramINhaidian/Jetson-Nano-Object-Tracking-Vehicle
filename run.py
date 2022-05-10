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
import nanocamera as nano

STD_LR = 0  # 左右
STD_UD = 0  # 上下
STD_QH = 0  # 前后

if __name__ == "__main__":
    bot = robot_control.myRobot()
    tof = distance.MyTOF()

    
    frame_queue = Queue(maxsize=5)
    darknet_image_queue = Queue(maxsize=5)
    detections_queue = Queue(maxsize=5) # same level
    distance_queue = Queue(maxsize=5) # same level
    order_queue = Queue(maxsize=5)
    pre_order_queue = Queue(maxsize=5)
    fps_queue = Queue(maxsize=5)

    darknet_config = {
        "input" : "nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM), width=(int)1280, height=720, format=NV12, framerate=30/1 ! nvvidconv filp=method=0 ! video/x-raw, width=1280, height=720, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink",
        "config_file" : "yolov4-tiny.cfg",
        "data_file"   : "coco.data",
        "weights"     : "yolov4-tiny.weights",
        "thresh"      : .25
    }

    def gstreamer_pipeline(
            capture_width=1280,
            capture_height=720,
            display_width=1280,
            display_height=720,
            framerate=60,
            flip_method=0
            ):
        return (
                "nvarguscamerasrc ! "
                "video/x-raw(memory:NVMM), "
                "width=(int)%d, height=(int)%d, "
                "format=(string)NV12, framerate=(fraction)%d/1 ! "
                "nvvidconv flip-method=%d ! "
                "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
                "videoconvert ! "
                "video/x-raw, format=(string)BGR ! appsink"
                )


    input_path = (
                'nvarguscamerasrc ! '
                'video/x-raw(memory:NVMM), '
                'width=(int)1280, height=(int)720, '
                'format=(string)NV12, framerate=(fraction)30/1 ! '
                'nvvidconv flip-method=0 ! '
                'video/x-raw, width=(int)1280, height=(int)720, format=(string)BGRx ! '
                'videoconvert ! '
                'video/x-raw, format=(string)BGR ! appsink'

            )
    network, class_names, class_colors = darknet.load_network(
            darknet_config["config_file"],
            darknet_config["data_file"],
            darknet_config["weights"],
            batch_size=1
        )
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    #input_path = darknet_config["input"]
    pack = [network, class_names, class_colors, width, height]
    #cap = nano.Camera(flip=0, width=1280, height=720, fps=30)
    cap = cv2.VideoCapture(input_path, cv2.CAP_GSTREAMER)
    #cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    # 前后 上下左右线程同步
    #cdt = Condition()

    # test
    # bot.begin_dance()

    # start
    Thread(target=yolo.video_capture, args=(cap, frame_queue, darknet_image_queue)).start()
        # frame_queue -> darknet_image_queue
    Thread(target=yolo.inference, args=(pack, cap, darknet_image_queue, detections_queue, fps_queue)).start()
        # darknet_image -> detections_queue
    Thread(target=distance.distance_measure, args=(cap, tof, distance_queue, pre_order_queue)).start()
        # -> distance_queue
    #Thread(target=distance.single_distance_measure, args=(tof, distance_queue, order_queue)).start()
    Thread(target=yolo.ver_hori_measure, args=(cap, detections_queue, pre_order_queue, order_queue)).start()
        # detections_qeue -> ver_hori_queue
    Thread(target=robot_control.robot_move, args=(order_queue, bot)).start()
        # 1.distance_queue 2. ver_hori_queue -> order_queue
        # order_queue transform
