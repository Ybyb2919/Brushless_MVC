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
    for index, row in table.iterrows():
        time = row['time']
        motor_id = int(row['motor_id'])
        if row['position'] is not None:
            if row['func'] is not None:
            commands.append(Command(time, motor_id, row['position'], None, None, row['kp'], row['kd']))
        elif row['speed'] is not None:
            commands.append(Command(time, motor_id, None, row['speed'], None, None, None))
        elif row['torque'] is not None:
            commands.append(Command(time, motor_id, None, None, row['torque'], None, None))
        else:
            raise ValueError(f"Empty command at row {index}")
    return commands
