from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import pandas
from typing import Optional, List


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
    prev_speed = False
    for index, row in table.iterrows():
        print(prev_speed)
        time = row['time']
        motor_id = int(row['motor_id'])
        if not pandas.isnull(row['position']):
            if prev_speed:
                commands.append(Command(time-0.2, 0, None, None, None, None, None))
                commands.append(Command(time-0.5, motor_id, None, 0, None, None, 0))
                ### when sending the second velocity command or any command after speed the motor does not accept it
            commands.append(Command(time, motor_id, row['position'], None, None, row['kp'], row['kd']))
            prev_speed = False
        elif not pandas.isnull(['speed']):
            commands.append(Command(time, motor_id, None, row['speed'], None, None, row['kd']))
            prev_speed = True
        elif row['torque'] is not None:
            commands.append(Command(time, motor_id, None, None, row['torque'], None, None))
        else:
            raise ValueError(f"Empty command at row {index}")
    return commands



# if __name__ == '__main__':
# run_from_xls(Path(sys.argv[1]), sys.argv[2])
# run_from_xls(Path('example.xlsx'), "COM3")
# run_from_xls(Path(sys.argv[1]), 'COM3')
