from jetbot import Robot
robot = Robot()
robot.left_motor.value = 0.8
# 0 - 1.0
robot.right_motor.value = 0.8


from servoserial import ServoSerial
servo_device = ServoSerial()
# 中央位置
servo_device.Servo_serial_control(1, 2100)
servo_device.Servo_serial_control(2, 2048)
# index = 1 : 左右方向  600 ~ 3600
# index = 2 : 上下方向  1300 ~ 4095