# from Model import Motor
import time
import Util1_Excel


class Controller:

    def send_once(motor_id, position, kp, kd ,COM_insert):
        with Motor.connect(COM_insert) as motor:
            print("SENDING")
            motor.select(int(motor_id))
            motor.set_position(float(position), float(kp), float(kd))
            print("EXECUTED")

    def run_from_xls(file_name, COM_insert):
        run_from_xls(file_name, COM_insert)
        print("Running from" + file_name)

    def run_from_xls_loop(file_name, COM_insert):
        print("Looping from : " + file_name)
        run_from_xls_loop(file_name, COM_insert)

    def turn_on(COM_insert):
        with Motor.connect(COM_insert) as motor:
            motor.init(1)
            time.sleep(1)
            motor.init(2)

    def read_position(COM_insert):
        try:
            with Motor.connect(COM_insert) as motor:
                return motor.read_position()
        except:
            print("Cannot read position")
            pass