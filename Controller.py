from Model import Motor
import time
import Util1_Excel
import sched
from Util1_Excel import Command
import schedule
from datetime import datetime

scheduler = sched.scheduler()
global loop_run
global loop_date


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
        turn_on(COM_insert)
        print("Building Scheduler")
        commands = Util1_Excel.read_xls(file_name)

        with Motor.connect(COM_insert) as motor:

            for command in commands:
                if command.motor_id == 0:
                    scheduler.enter(command.time, priority=0, action=set_zero, argument=('COM3'))
                scheduler.enter(command.time, priority=0,
                                action=run_command, argument=(motor, command))
            time.sleep(0.3)
            print("Running from: " + file_name)
            print("--- STARTING SEQUENCE ---")
            scheduler.run()

        print("--- GO TO ZERO & OFF ---")
        go_to_zero_off(COM_insert)

        print("--- END OF SEQUENCE ---")
    except:
        print("Can not run sequence from .xls file")
        pass


def run_from_xls_loop(file_name, COM_insert, loop_count):
    try:
        i = int(loop_count)
        turn_on(COM_insert)
        print("Building Scheduler")
        commands = Util1_Excel.read_xls(file_name)

        print("Running from: " + file_name)

        with Motor.connect(COM_insert) as motor:
            global loop_run
            loop_run = True
            while i > 0 and loop_run is True:
                i -= 1
                for command in commands:
                    scheduler.enter(command.time, priority=0,
                                    action=run_command, argument=(motor, command))
                time.sleep(0.3)
                print("Iteration", int(loop_count) - i)
                scheduler.run()

        print("--- GO TO ZERO & OFF ---")
        go_to_zero_off(COM_insert)

        print("--- END OF SEQUENCE ---")
    except:
        print("Can not run loop from .xls file")
        pass


def run_from_xls_loop_date(file_name, COM_insert, loop_count, start_hour, end_hour):
    if file_name == "":
        print("No file chosen, please choose file to run")
    else:
        # schedule.every().day.at(start_hour).do(job_func=run_from_xls_loop_time,
        #                                        file_name=file_name, COM_insert=COM_insert, end_hour=end_hour)
        schedule.every(5).seconds.do(job_func=run_from_xls_loop_time,
                                     file_name=file_name, COM_insert=COM_insert,
                                     start_hour=start_hour, end_hour=end_hour)
        now = datetime.now()
        start_date = int(now.strftime("%d"))
        num_days = int(loop_count)
        turn_on(COM_insert)
        global loop_date
        loop_date = True

        while start_date + num_days > int(now.strftime("%d")) and loop_date:
            print("test1", datetime.now())
            schedule.run_pending()
            time.sleep(5)
        schedule.clear()
        go_to_zero_off(COM_insert)



def run_from_xls_loop_time(file_name, COM_insert, start_hour, end_hour):
    end_hour = end_hour[:2]
    start_hour = start_hour[:2]
    try:
        global loop_run
        loop_run = True
        i = 1
        while int(start_hour) < int(datetime.now().strftime("%H")) < int(end_hour) and loop_run:
            with Motor.connect(COM_insert) as motor:
                print("Building Scheduler")
                commands = Util1_Excel.read_xls(file_name)

                print("Running from: " + file_name)
                for command in commands:
                    scheduler.enter(command.time, priority=0, action=run_command, argument=(motor, command))
                time.sleep(0.3)
                print("Iteration: ", i)
                scheduler.run()
                i += 1
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


def set_zero(COM_insert):
    try:
        print("Setting current position to ZERO")
        with Motor.connect(COM_insert) as motor:
            motor.select(1)
            motor.reset()
            motor.select(2)
            motor.reset()
    except:
        print("Can not set position to ZERO - unknown problem")
        pass

def go_to_zero_off(COM_insert):
    try:
        print("Reset to zero position and turning off")
        stop_scheduler()
        time.sleep(1)
        with Motor.connect(COM_insert) as motor:
            time.sleep(0.25)
            motor.select(1)
            motor.go_to_zero_off()
            time.sleep(0.5)

            motor.select(2)
            motor.go_to_zero_off()
        print("Motors OFF")
    except:
        print("Could not turn off motors")
        pass


def stop_date_loop(COM_insert):
    try:
        print("Stopping loop and turning motors off")
        global loop_date
        loop_date = False
        go_to_zero_off(COM_insert)
    except:
        print("Could not stop loop")
        pass


def stop_scheduler():
    global loop_run
    loop_run = False
    list(map(scheduler.cancel, scheduler.queue))
    time.sleep(1)
