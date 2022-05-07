from servoserial import ServoSerial

def appropriate_position():
    servo_device = ServoSerial()
    #servo_device.Servo_serial_double_control(1, 2100, 2, 2048)
    #servo_device.Servo_serial_control(2,2048)
    #servo_device.Servo_serial_control(1,1700)
    servo_device.Servo_serial_control(2,1900)

sd = ServoSerial()
sd.Servo_serial_control(2,1900)
sd = ServoSerial()
sd.Servo_serial_control(2,2500)

