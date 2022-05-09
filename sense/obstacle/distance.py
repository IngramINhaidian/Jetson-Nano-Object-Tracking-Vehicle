# VL53L0X Laser Ranging Sensor (Produced by Yahboom)

import time
#import VL53L0X
from . import VL53L0X
import cv2
#import obstacle.VL53L0X as VL53L0X

class Order():
    def __init__(self, \
        error_rl=0, error_ud=0, error_qh=0,\
        beta_l=0, beta_r=0, alpha=0, gamma=0):
        self.error_rl = error_rl
        self.error_ud = error_ud
        self.error_qh = error_qh
        self.br = beta_r
        self.al = alpha
        self.ga = gamma
        self.bl = beta_l
        self.br = beta_r
        self.al = alpha
        self.ga = gamma

class MyTOF(VL53L0X.VL53L0X):
    def __init__(self):
        super(MyTOF, self).__init__()
        self.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
    
    def range(self):
        timing = self.get_timing()
        if (timing < 20000):
            timing = 20000
        distance = self.get_distance()
        return distance, timing

    # def run(self):
    #     while True:
    #         dist, t = self.range()
    #         time.sleep(t / 100000.00)
    
    def destroy(self):
        self.stop_ranging()

EXPECTED_DIST = 10
def distance_measure(sensor, distance_queue, order_queue):
    while cap.isOpened():
        dist, t = sensor.range()
        # distance_queue.put(dist)
        # time.sleep(t / 100000.00)
        error_qh = dist - EXPECTED_DIST
        order = Order(error_qh=error_qh)
        order_queue.put(order)
        if cv2.waitKey(fps) == 27:
            break
    cap.release()
    sensor.destroy()



if __name__ =="__main__":
    my_tof = MyTOF()
    for i in range(1, 101):
        dist, t = my_tof.range()
        #time.sleep(0.001)
        print(dist)
        time.sleep(t / 100000.00)
    my_tof.destroy()
