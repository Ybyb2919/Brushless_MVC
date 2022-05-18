from cgitb import reset
from dataclasses import dataclass
from datetime import datetime
from os import read
from pathlib import Path
import random
from tracemalloc import start
from Model import Motor
import sys
import pandas
from typing import Optional, List
import time
import sched
import Controller


@dataclass
class Command:
    time: datetime
    motor_id: int
    position: Optional[float]
    speed: Optional[float]
    torque: Optional[float]
    kp: Optional[float]
    kd: Optional[float]


def read_xls(file: Path) -> List[Command]:
    table = pandas.read_excel(file)
    commands = []
    for index, row in table.iterrows():
        time = row['time']
        motor_id = int(row['motor_id'])
        if row['position'] is not None:
            commands.append(Command(time, motor_id, row['position'], None, None, row['kp'], row['kd']))
        elif row['speed'] is not None:
            commands.append(Command(time, motor_id, None, row['speed'], None, None, None))
        elif row['torque'] is not None:
            commands.append(Command(time, motor_id, None, None, row['torque'], None, None))
        else:
            raise ValueError(f"Empty command at row {index}")
    return commands


def run_command(motor: Motor, command: Command):
    motor.select(command.motor_id)

    if command.position is not None:
        motor.set_position(command.position, command.kp, command.kd)
    elif command.speed is not None:
        motor.set_speed(command.speed)
    else:
        motor.set_torque(command.torque)


scheduler = sched.scheduler()


def run_from_xls(file: Path, com_port: str):
    commands = read_xls(file)
    motor_ids = {command.motor_id for command in commands}

    with Motor.connect(com_port) as motor:
        print("--- INIT MOTORS ---")

        for motor_id in motor_ids:
            motor.init(motor_id)

        for command in commands:
            scheduler.enter(command.time, priority=0, action=run_command, argument=(motor, command))

        print("--- STARTING SEQUENCE ---")
        scheduler.run()

        # Moves to zero:
        print("--- GO TO ZERO & OFF ---")
        Controller.go_to_zero_off()

        Controller.go_to_zero_off()

        print("--- END OF SEQUENCE ---")


def run_from_xls_loop(file: Path, com_port: str):
    commands = read_xls(file)
    motor_ids = {command.motor_id for command in commands}

    with Motor.connect(com_port) as motor:
        print("--- INIT MOTORS ---")

        for motor_id in motor_ids:
            motor.init(motor_id)
        print("--- STARTING LOOP ---")

        global loop_run
        loop_run = True
        x = 0

        while loop_run:
            print("Loop iteration :", x)
            x += 1
            for command in commands:
                scheduler.enter(command.time, priority=0, action=run_command, argument=(motor, command))
            scheduler.run()
            time.sleep(1)


def stop_scheduler():
    global loop_run
    loop_run = False
    list(map(scheduler.cancel, scheduler.queue))


# if __name__ == '__main__':
# run_from_xls(Path(sys.argv[1]), sys.argv[2])
# run_from_xls(Path('example.xlsx'), "COM3")
# run_from_xls(Path(sys.argv[1]), 'COM3')