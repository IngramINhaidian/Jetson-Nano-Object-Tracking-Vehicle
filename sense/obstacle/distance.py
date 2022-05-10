# VL53L0X Laser Ranging Sensor (Produced by Yahboom)

import time
#import VL53L0X
from . import VL53L0X
import cv2
#import obstacle.VL53L0X as VL53L0X

KP = 1
KI = 1
KD = 1

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

    def PID(self, last_e_rl, last_e_ud, last_e_qh):
        error_sum_rl = self.error_rl + last_e_rl
        rl = KP * self.error_rl + KI * error_sum_rl + KD * (self.error_rl - last_e_rl)
        error_sum_ud = self.error_ud + last_e_ud
        ud = KP * self.error_ud + KI * error_sum_ud + KD * (self.error_ud - last_e_ud)
        error_sum_qh = self.error_qh + last_e_qh
        qh = KP * self.error_qh + KI * error_sum_qh + KD * (self.error_qh - last_e_qh)
        print("rl: ", rl)
        print("ud: ", ud)
        print("qh: ", qh)
        return [rl, ud, qh]


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
def distance_measure(cap, sensor, distance_queue, pre_order_queue):
    while True:
        dist, t = sensor.range()
        # distance_queue.put(dist)
        # time.sleep(t / 100000.00)
        error_qh = dist - EXPECTED_DIST
        order = Order(error_qh=error_qh)
        print("Stuck pre_order_queue & distance_measure")
        if not pre_order_queue.full():
            pre_order_queue.put(order)
        else:
            print("unable to put new elements into pre_order_queue")
        time.sleep(0.01)
        if cv2.waitKey() == 27:
            break
    cap.release()
    sensor.destroy()

# def single_distance_measure(sensor, distance_queue, order_queue):
#     while True:
#         dist, t = sensor.range()
#         error_qh = dist - EXPECTED_DIST

#         order = Order(error_qh=error_qh)
#         order_queue.put(order)



if __name__ =="__main__":
    my_tof = MyTOF()
    for i in range(1, 101):
        dist, t = my_tof.range()
        #time.sleep(0.001)
        print(dist)
        time.sleep(t / 100000.00)
    my_tof.destroy()
