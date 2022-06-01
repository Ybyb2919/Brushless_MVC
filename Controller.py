from Model import Motor
import time
import Util1_Excel
import sched
from Util1_Excel import Command

scheduler = sched.scheduler()

class Controller:

    def send_once(motor_id, position, kp, kd, COM_insert):
        try:
            with Motor.connect(COM_insert) as motor:
                print("SENDING")
                motor.select(int(motor_id))
                motor.set_position(float(position), float(kp), float(kd))
                print("EXECUTED")
        except:
            print("Can not execute single command")
            pass

    def run_command(COM_insert, command: Command):
        with Motor.connect(COM_insert) as motor:
            motor.select(command.motor_id)
        if command.position is not None:
            motor.set_position(command.position, command.kp, command.kd)
        elif command.speed is not None:
            motor.set_speed(command.speed)
        else:
            motor.set_torque(command.torque)

    def run_from_xls(file_name, COM_insert):
        # running from commands
        # try:
            Controller.turn_on(COM_insert)
            print("Building Scheduler")

            commands = Util1_Excel.read_xls(file_name)

            motor_ids = {command.motor_id for command in commands}
            print("--- INIT MOTORS ---")

            with Motor.connect(COM_insert) as motor:
                Controller.turn_on(COM_insert)
                time.sleep(7)

                for command in commands:
                    scheduler.enter(command.time, priority=0, action=Controller.run_command, argument=(COM_insert, command))
            print("Running from" + file_name)
            # print(scheduler.queue)
            scheduler.run()
            print("--- STARTING SEQUENCE ---")

            # Moves to zero:
            print("--- GO TO ZERO & OFF ---")
            Controller.go_to_zero_off(COM_insert)

            print("--- END OF SEQUENCE ---")
        # except:
            print("Cannont run sequence from .xls file")
            # pass

    def run_from_xls_loop(file_name, COM_insert):
        # try:
            print("Looping from : " + file_name)
        #     run_from_xls_loop(file_name, COM_insert)
        #
        # except:
        #     print("Cannont run loop from .xls file")
        #     pass

    def turn_on(COM_insert):
        try:
            print("Turning on")
            with Motor.connect(COM_insert) as motor:
                motor.init(1)
                time.sleep(1)
                motor.init(2)
            print("Motors ON")
        except:
            print("Can not Turn on motors")
            print("Please initially run motors using an excel file (temporary)")
            pass

    def read_position(COM_insert):
        try:
            with Motor.connect(COM_insert) as motor:
                return motor.read_position()
        except:
            print("Cannot read position")
            pass

    def go_to_zero_off(COM_insert):
        try:
            print("Reset to zero position and turning off")
            Controller.stop_scheduler()
            time.sleep(1)
            with Motor.connect(COM_insert) as motor:
                time.sleep(0.25)
                motor.select(1)
                motor.go_to_zero_off()

                motor.select(2)
                motor.go_to_zero_off()
            print("Motors OFF")
        except:
            print("Could not turn off motors")
            pass

    @staticmethod
    def stop_scheduler():
        global loop_run
        loop_run = False
        list(map(scheduler.cancel, scheduler.queue))