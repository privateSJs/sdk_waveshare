from transport.serial import SerialTransport
from bus_servo_driver import ServoBusDriver
from protocol.protocol import SCSRegister
import time

driver = ServoBusDriver("COM14", baudrate=1000000)

driver.connect()
try:
    st = driver.protocol.ping(1)
    print("PING OK:", st)

    st = driver.go_to_position(servo_id=1, position=0, speed=2400, acc=100)
    print("Command GO TO POSITION:", st)
    time.sleep(5)

    st = driver.go_to_position(servo_id=1, position=1000, speed=2400, acc=100)
    print("Command GO TO POSITION:", st)
    time.sleep(5)

    st = driver.go_to_position(servo_id=1, position=2000, speed=2400, acc=100)
    print("Command GO TO POSITION:", st)
    time.sleep(5)

    st = driver.go_to_position(servo_id=1, position=300, speed=2400, acc=100)
    print("Command GO TO POSITION:", st)
    time.sleep(5)

    st = driver.go_to_position(servo_id=1, position=3500, speed=2400, acc=100)
    print("Command GO TO POSITION:", st)
    time.sleep(5)

    st = driver.get_position(servo_id=1)
    print("Position value:", st)

    st = driver.get_speed(servo_id=1)
    print("Speed value:", st)

    st = driver.get_temperature(servo_id=1)
    print("Temperature value:", st)

    st = driver.get_voltage(servo_id=1)
    print("Voltage value:", st)

    st = driver.get_load(servo_id=1)
    print("Load value:", st)

    st = driver.get_current(servo_id=1)
    print("Current value:", st)

finally:
    driver.disconnect()
