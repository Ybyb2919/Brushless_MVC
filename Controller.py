from Model import Motor
import time
import Util1_Excel
import sched
from Util1_Excel import Command
import schedule
from datetime import datetime
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

    def run_command(motor: Motor, command: Command):
        motor.select(command.motor_id)

        if command.position is not None:
            motor.set_position(command.position, command.kp, command.kd)
        elif command.speed is not None:
            motor.set_speed(command.speed)
        else:
            motor.set_torque(command.torque)

    def run_from_xls(file_name, COM_insert):
        try:
            Controller.turn_on(COM_insert)
            print("Building Scheduler")
            commands = Util1_Excel.read_xls(file_name)

            with Motor.connect(COM_insert) as motor:

                for command in commands:
                    scheduler.enter(command.time, priority=0,
                                    action=Controller.run_command, argument=(motor, command))
                time.sleep(2)
                print("Running from" + file_name)
                print("--- STARTING SEQUENCE ---")
                scheduler.run()

            print("--- GO TO ZERO & OFF ---")
            Controller.go_to_zero_off(COM_insert)

            print("--- END OF SEQUENCE ---")
        except:
            print("Can not run sequence from .xls file")
            pass

    def run_from_xls_loop(file_name, COM_insert, loop_count):
        try:
            i = int(loop_count)
            Controller.turn_on(COM_insert)
            print("Building Scheduler")
            commands = Util1_Excel.read_xls(file_name)

            print("Running from" + file_name)

            with Motor.connect(COM_insert) as motor:
                while i > 0 and loop_run is True:
                    i -= 1
                    for command in commands:
                        scheduler.enter(command.time, priority=0,
                                        action=Controller.run_command, argument=(motor, command))
                    time.sleep(0.3)
                    print("Iteration", int(loop_count) - i)
                    scheduler.run()

            print("--- GO TO ZERO & OFF ---")
            Controller.go_to_zero_off(COM_insert)

            print("--- END OF SEQUENCE ---")
        except:
            print("Can not run loop from .xls file")
            pass

    def run_from_xls_loop_date(file_name, COM_insert, loop_count, start_hour, end_hour):
        schedule.every().day.at(start_hour).do(Controller.run_from_xls_loop_time
                                               (file_name,COM_insert,end_hour))
        start_date = now.strftime("%d")
        Controller.turn_on(COM_insert)

        while int(loop_count)+int(start_date)<int(now.strftime("%D")):




    @staticmethod
    def run_from_xls_loop_time(file_name, COM_insert, end_hour):
        end_hour = end_hour[:2]
        now = datetime.now()
        current_hour = now.strftime("%H")
        try:
            Controller.turn_on(COM_insert)
            print("Building Scheduler")
            commands = Util1_Excel.read_xls(file_name)
            print("Running from" + file_name)

            with Motor.connect(COM_insert) as motor:
                while int(current_hour) < int(end_hour):
                    for command in commands:
                        scheduler.enter(command.time, priority=0,
                                        action=Controller.run_command, argument=(motor, command))
                    time.sleep(0.3)
                    print("Iteration: ", i)
                    scheduler.run()

            print("--- GO TO ZERO & OFF ---")
            Controller.go_to_zero_off(COM_insert)

            print("--- END OF SEQUENCE ---")
        except:
            print("Can not run loop from .xls file")
            pass

    def turn_on(COM_insert):
        try:
            print("Turning on")
            with Motor.connect(COM_insert) as motor:
                motor.init(1)
                time.sleep(1)
                motor.init(2)
            print("Motors ON")
        except:
            print("Can not Turn on motors. Check Motors arent on and if they are reset the system")
            pass

    def read_position(COM_insert, motor_id):
        try:
            with Motor.connect(COM_insert) as motor:
                motor.select(motor_id)
                return motor.return_position()
        except:
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
