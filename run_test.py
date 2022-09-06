import time

import Controller
from Model import Motor

if __name__ == '__main__':
    # Controller.turn_on('COM3')
    # time.sleep(3.5)
    # print(Controller.read_position('COM3', 1))
    # with Motor.connect('COM3') as motor:
        # time.sleep(0.25)
        # motor.select()
        # motor.set_position(10, 2, 2)

    time.sleep(2)
    print(Controller.read_position('COM3', 2))

    print('finished test')


