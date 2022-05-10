from cgi import test
from tkinter.font import BOLD
import PySimpleGUI as sg
import os.path
# from brushless import Motor
import time
import logging
from multiprocessing import Process
# from read_table_new import run_from_xls, run_from_xls_loop, stop_scheduler
import threading
import Controller


def the_gui():
    sg.theme('tealmono')

    position_test_demo = [
        [
            sg.Text("Please choose USB port: "),
            sg.Combo(['COM3', 'COM6', 'COM7'], default_value='COM3', size=(10, 1), key='-COM-')

        ],
        [
            sg.Text("Position test controller: ", font=BOLD)
        ],
        [
            sg.Text("Motor ID:"),
            sg.Combo(['1', '2'], default_value='1', key='-MOTORID-')
        ],
        [
            sg.Text("Position:"),
            sg.In(size=(5, 1), key="-POSITION-"),
            sg.Text("0-99")

        ],
        [
            sg.Text("Kp:        "),
            sg.In(size=(5, 1), key="-KP-"),
            sg.Text("0-500")
        ],
        [
            sg.Text("Kd:        "),
            sg.In(size=(5, 1), key="-KD-"),
            sg.Text("0-5")

        ],
        [
            sg.Button("TURN ON"),
            sg.Button("SEND ONCE"),
            sg.Button("STOP")
        ]

    ]

    file_list_column = [
        [
            sg.Text("Table Folder"),
            sg.In(size=(21, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(
                values=[], enable_events=True, size=(40, 10), key="-TABLE LIST-"
            )
        ],
    ]

    file_run_section = [
        [
            sg.Text("Current Position: "),
            # sg.Text(size=(30, 1), text=Controller.read_position('COM3')),
        ],
        [
            sg.Text("The file chosen is: "),
            sg.In(size=(28, 1), key="-TOUT-")
        ],
        [
            sg.HSeparator(10)
        ],
        [
            sg.Text("                         "),
            sg.Button("RUN"),
            sg.Button("MOTOR STOP")
        ],
        [
            sg.HSeparator()
        ],
        [
            sg.Text("Hit EXIT to terminate the program:"),
            sg.Button('EXIT', font='Helvetica 12 bold italic', button_color=('black', 'red'), border_width=0, ),
        ],
        [
            sg.Text("Run file as loop: "),
            sg.Button("LOOP")
        ]
    ]

    layout = [
        [
            sg.Column(position_test_demo),
            sg.VSeparator(),
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(file_run_section)
        ]
        ,
        [sg.Output(size=(132,15))]
    ]

    window = sg.Window('AK 60 Duo Controller', layout)

    while True:
        event, values = window.read()

        if event == "EXIT" or event == sg.WIN_CLOSED:
            break

        elif event == "TURN ON":
            try:
                threading.Thread(target=Controller.turn_on, args=(values['-COM-'],), daemon=True).start()
            except:
                print("Cannont Turn on motors")
                print("Please initially run motors using an excel file (temporary)")
                pass

        elif event == "SEND ONCE":
            try:
                position = values['-POSITION-']
                kp = values['-KP-']
                kd = values['-KD-']
                threading.Thread(target=Controller.send_once, args=(values['-MOTORID-'], position, kp, kd, values['-COM-'],), daemon=True).start()
            except:
                print("Can not execute single command")
                pass

        elif event == "STOP":
            try:
                print("--- GO TO ZERO & OFF ---")
                stop_scheduler()
                with Motor.connect(values['-COM-']) as motor:

                    motor.select(1)
                    motor.go_to_zero_off()

                    motor.select(2)
                    motor.go_to_zero_off()
            except:
                pass

        elif event == "MOTOR STOP":
            try:
                print("--- GO TO ZERO & OFF ---")
                stop_scheduler()
                time.sleep(1)
                with Motor.connect(values['-COM-']) as motor:
                    time.sleep(0.25)
                    motor.select(1)
                    motor.go_to_zero_off()

                    motor.select(2)
                    motor.go_to_zero_off()
            except:
                pass

        elif event == "-FOLDER-":
            folder = values["-FOLDER-"]
            try:
                file_list = os.listdir(folder)
            except:
                file_list = []

            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                   and f.lower().endswith((".xlsx"))
            ]
            window["-TABLE LIST-"].update(fnames)

        elif event == "-TABLE LIST-":
            try:
                filename = os.path.join(
                    values["-FOLDER-"], values["-TABLE LIST-"][0]
                )
                window["-TOUT-"].update(filename)
            except:
                pass

        elif event == "RUN":
            try:
                threading.Thread(target=Controller.run_from_xls, args=(values['-TOUT-'], values['-COM-']),
                                 daemon=True).start()
            except:
                print("Cannont run sequence from .xls file")
                pass

        elif event == "LOOP":
            try:
                threading.Thread(target=Controller.run_from_xls_loop, args=(values['-TOUT-'], values['-COM-']),
                                 daemon=True).start()
            except:
                print("Cannont run loop from .xls file")
                pass


if __name__ == '__main__':
    the_gui()
    print('EXITING PROGRAM')
    time.sleep(0.5)