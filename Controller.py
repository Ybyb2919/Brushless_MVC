from Model import Motor
import time
import Util1_Excel
import sched
from Util1_Excel import Command
import schedule
from datetime import datetime


class Controller:

    def __init__(self):
        self.loop_date = None
        self.loop_run = None
        self.scheduler = sched.scheduler()

    @staticmethod
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

    def run_command(self, motor: Motor, command: Command):
        motor.select(command.motor_id)

        if command.motor_id == 0:
            motor.select(1)
            motor.reset()
            motor.select(2)
            motor.reset()
        elif command.position is not None:
            motor.set_position(command.position, command.kp, command.kd)
        elif command.speed is not None:
            motor.set_speed(command.speed, command.kd)
        else:
            motor.set_torque(command.torque)

    def run_from_xls(self, file_name, COM_insert):
        try:
            print("Building Scheduler")
            commands = Util1_Excel.read_xls(file_name)

            with Motor.connect(COM_insert) as motor:
                for command in commands:
                    if command.motor_id == 0:
                        print(self.scheduler)
                        self.scheduler.enter(command.time, priority=0, action=self.run_command, argument=(motor, command))
                    self.scheduler.enter(command.time, priority=0, action=self.run_command, argument=(motor, command))
                time.sleep(0.1)
                print("Running from: " + file_name)
                print("--- STARTING SEQUENCE ---")
                self.scheduler.run()
            print("--- END OF SEQUENCE ---")
        except Exception as e:
            print("Can not run sequence from .xls file")
            print(e)

    # Looping from XLS does not zero positions between iterations and does not stop velocity commands
    def run_from_xls_loop(self, file_name, COM_insert, loop_count):
        try:
            i = int(loop_count)
            print("Building Scheduler")
            commands = Util1_Excel.read_xls(file_name)

            print("Running from: " + file_name)

            with Motor.connect(COM_insert) as motor:
                self.loop_run = True
                while i > 0 and self.loop_run is True:
                    i -= 1
                    for command in commands:
                        self.scheduler.enter(command.time, priority=0,
                                             action=self.run_command, argument=(motor, command))
                    time.sleep(0.3)
                    print("Iteration", int(loop_count) - i)
                    self.scheduler.run()
            print("--- END OF LOOP ---")
        except Exception as e:
            print("Can not run loop from .xls file")
            print(e)

    def run_from_xls_loop_time(self, file_name, COM_insert, start_hour, end_hour):
        end_hour = end_hour[:2]
        start_hour = start_hour[:2]
        try:
            self.loop_run = True
            i = 1
            while int(start_hour) < int(datetime.now().strftime("%H")) < int(end_hour) and self.loop_run:
                with Motor.connect(COM_insert) as motor:
                    print("Building Scheduler")
                    commands = Util1_Excel.read_xls(file_name)

                    print("Running from: " + file_name)
                    for command in commands:
                        self.scheduler.enter(command.time, priority=0, action=self.run_command, argument=(motor, command))
                    time.sleep(0.3)
                    print("Iteration: ", i)
                    self.scheduler.run()
                    i += 1
        except Exception as e:
            print("Can not run loop from .xls file")
            print(e)

    def run_from_xls_loop_date(self, file_name, COM_insert, loop_count, start_hour, end_hour):
        if file_name == "":
            print("No file chosen, please choose file to run")
        else:
            # schedule.every().day.at(start_hour).do(job_func=run_from_xls_loop_time,
            #                                        file_name=file_name, COM_insert=COM_insert, end_hour=end_hour)
            schedule.every(5).seconds.do(job_func=self.run_from_xls_loop_time,
                                         file_name=file_name, COM_insert=COM_insert,
                                         start_hour=start_hour, end_hour=end_hour)
            now = datetime.now()
            start_date = int(now.strftime("%d"))
            num_days = int(loop_count)
            self.motors_on(COM_insert)
            self.loop_date = True

            while start_date + num_days > int(now.strftime("%d")) and loop_date:
                print("test1", datetime.now())
                schedule.run_pending()
                time.sleep(5)

    def motors_on(self, COM_insert):
        try:
            print("Turning on")
            with Motor.connect(COM_insert) as motor:
                motor.init(1)
                motor.init(2)
            print("MOTORS ON")
        except Exception as e:
            print("Can not Turn on motors. Check Motors arent on and if they are reset the system")
            print(e)

    @staticmethod
    def motors_off(COM_insert):
        try:
            with Motor.connect(COM_insert) as motor:
                motor.select(1)
                motor.stop()
                motor.select(2)
                motor.stop()
            print("MOTORS OFF")
        except Exception as e:
            print("Can not turn motors off")
            print(e)

    def interfere(self, file_name, COM_insert, loop_count, inter_file):
        try:
            print("Encountered interference! Running interference sequence")
            self.stop_run(COM_insert)
            self.set_position_zero(COM_insert)
            self.run_from_xls(inter_file, COM_insert)
            time.sleep(0.5)
            self.run_from_xls_loop(file_name, COM_insert, loop_count)
        except:
            try:
                print("Can not run " + inter_file + " returning to loop " + file_name)
                self.run_from_xls_loop(file_name, COM_insert, loop_count)

            except Exception as e:
                print("Stuck, please restart!")
                print(e)

    def stop_run(self, COM_insert):
        try:
            self.stop_scheduler()
            time.sleep(0.2)
            print("RUN STOPPED")
        except Exception as e:
            print("Could not stop run")
            print(e)

    def stop_date_loop(self, COM_insert):
        try:
            global loop_date
            loop_date = False
            self.stop_run(COM_insert)
        except:
            print("Could not stop loop")

    @staticmethod
    def set_position_zero(COM_insert):
        try:
            with Motor.connect(COM_insert) as motor:
                motor.select(1)
                motor.set_position(0, 3, 1)
                motor.select(2)
                motor.set_position(0, 3, 1)
            print("GO TO ZERO")
        except Exception as e:
            print("Can not set position to ZERO")
            print(e)

    @staticmethod
    def set_speed_zero(COM_insert):
        try:
            with Motor.connect(COM_insert) as motor:
                motor.select(1)
                motor.set_speed(0, 0)
                motor.select(2)
                motor.set_speed(0, 0)
            print("SPEED ZERO")
        except Exception as e:
            print("Can not set speed to ZERO")
            print(e)

    @staticmethod
    def position_zero(COM_insert):
        try:
            with Motor.connect(COM_insert) as motor:
                motor.select(1)
                motor.reset()
                motor.set_position(0, 0, 0)
                motor.select(2)
                motor.reset()
                motor.set_position(0, 0, 0)
        except Exception as e:
            print("Can not zero position")
            print(e)

    def stop_scheduler(self):
        self.loop_run = False
        list(map(self.scheduler.cancel, self.scheduler.queue))
        time.sleep(1)
