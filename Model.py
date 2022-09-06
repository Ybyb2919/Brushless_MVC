from serial import Serial
from config import AK606Config
from contextlib import contextmanager
from fields import Field
import time

global current_position

class Motor:
    RLINK_PREFIX = bytes.fromhex('aaaf0fa1')
    STARTUP_RLINK_MESSAGE = bytes.fromhex('aaaf07a2a101a4')

    def __init__(self, serial, motor_id=0):
        self.serial = serial
        self.motor_id = motor_id

    @classmethod
    @contextmanager
    def connect(cls, port_name: str, baud_rate=921600):
        with Serial(port=port_name, baudrate=baud_rate) as ser:
            ser.write(cls.STARTUP_RLINK_MESSAGE)
            ser.read(7)
            yield cls(ser)

    @staticmethod
    def _calc_checksum(data: bytes):
        return (sum(data) & 0xff).to_bytes(1, 'big')

    def send_message(self, can_data):
        data = self.RLINK_PREFIX + can_data + self.motor_id.to_bytes(1, 'big') + b'\1'
        message = data + self._calc_checksum(data)
        self.serial.write(message)
        response = self.serial.read(11)
        response_can_data = response[4:-1]
        print('ID: %d = ' % self.motor_id, end='')
        print(Field.unpack(response_can_data, [AK606Config.POSITION, AK606Config.SPEED]))
        position = (Field.unpack(response_can_data, [AK606Config.POSITION]))
        position = float((str(position[0]).split(':')[1])[0:15])
        global current_position
        current_position = position


    def init(self, motor_id):
        """ init motor by id"""
        self.select(motor_id)
        self.start()  # enable motor
        time.sleep(1)
        self.reset()  # goto zero
        time.sleep(1)
        self.set_speed(0, 0)

    def select(self, motor_id):
        """ select motor id"""
        self.motor_id = motor_id

    def start(self):
        """ start motor """
        self.send_message(bytes.fromhex('fffffffffffffffc'))

    def stop(self):
        """ stop motor """
        self.send_message(bytes.fromhex('fffffffffffffffd'))

    def reset(self):
        """ reset motor """
        self.send_message(bytes.fromhex('fffffffffffffffe'))
        self.go_to_zero()

    def set_position(self, position, kp, kd):
        self.send_message(AK606Config(position=position, speed=0, kp=kp, kd=kd, torque=0).can_data)

    def set_speed(self, speed, kd):
        self.send_message(AK606Config(position=0, speed=speed, kp=0, kd=kd, torque=0).can_data)

    def set_torque(self, torque, kd=0.2):
        self.send_message(AK606Config(position=0, speed=0, kp=0, kd=kd, torque=torque).can_data)

    def go_to_zero(self, position=0, kp=15, kd=4):
        self.send_message(AK606Config(position=position, speed=0, kp=kp, kd=kd, torque=0).can_data)
        time.sleep(1)

    def go_to_zero_off(self):
        self.go_to_zero()
        time.sleep(0.5)
        self.stop()
        time.sleep(0.5)

    def position_read(self, motor_id):
        while True:
            try:
                global current_position
                Motor.select(self, motor_id)
                Motor.set_position(self, position=0, kp=0, kd=0)
                # print(current_position)
                return current_position
            except:
                pass


    # def read_speed(self):
    #     return AK606Config.SPEED

    # def read_torque(self):
    #     return AK606Config.TORQUE

