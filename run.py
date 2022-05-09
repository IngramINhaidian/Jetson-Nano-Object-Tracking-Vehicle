from queue import Queue
from control import servoserial
from control import robot_control
from sense.obstacle import distance
from threading import Thread, enumerate, Condition
#from sense import obstacle
from sense import visual
from sense.obstacle import distance
from sense.visual import yolo


STD_LR = 0  # 左右
STD_UD = 0  # 上下
STD_QH = 0  # 前后

if __name__ == "__main__":
    bot = robot_control.myRobot()
    tof = distance.my_tof()

    
    frame_queue = Queue()
    darknet_image_queue = Queue()
    detections_queue = Queue() # same level
    distance_queue = Queue(maxsize=1) # same level
    order_queue = Queue(maxsize=1)

    # 前后 上下左右线程同步
    cdt = Condition()

    # test
    # bot.begin_dance()

    # start
    Thread(target=yolo.video_capture, args=(frame_queue, darknet_image_queue)).start()
        # frame_queue -> darknet_image_queue
    Thread(target=yolo.inference, args=(darknet_image_queue, detections_queue)).start()
        # darknet_image -> detections_queue
    Thread(target=distance.distance_measure, args=(tof, distance_queue, order_queue)).start()
        # -> distance_queue
    Thread(target=yolo.ver_hori_measure, args=(detections_queue, order_queue)).start()
        # detections_qeue -> ver_hori_queue
    Thread(target=robot_control.robot_move, args=(order_queue, bot)).start()
        # 1.distance_queue 2. ver_hori_queue -> order_queue
        # order_queue transform
