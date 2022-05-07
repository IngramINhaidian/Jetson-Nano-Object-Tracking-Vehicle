# VL53L0X Laser Ranging Sensor (Produced by Yahboom)

import time
import sense.obstacle.VL53L0X as VL53L0X

class MyTOF(VL53L0X.VL53L0X):
    def __init__(self):
        super(MyTOF, self).__init__()
        self.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
    
    def range(self):
        timing = self.get_timing()
        if (timing < 20000):
            timing = 20000
        distance = self.get_distance()
        return distance, time

    # def run(self):
    #     while True:
    #         dist, t = self.range()
    #         time.sleep(t / 100000.00)
    
    def destroy(self):
        self.stop_ranging()
    
        


if __name__ =="__main__":
    my_tof = MyTOF()
    for i in range(1, 101):
        dist, t = my_tof.range()
        time.sleep(t / 100000.00)
    my_tof.destroy()
