from tkinter.font import BOLD
import PySimpleGUI as sg
import os.path
import time
import threading
from Controller import Controller


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
            sg.HSeparator()
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
        [sg.Output(size=(132, 15))]
    ]

    window = sg.Window('AK 60 Duo Controller', layout)

    while True:
        event, values = window.read()

        if event == "EXIT" or event == sg.WIN_CLOSED:
            break

        elif event == "TURN ON":
            threading.Thread(target=Controller.turn_on, args=(values['-COM-'],), daemon=True).start()

        elif event == "SEND ONCE":
            position = values['-POSITION-']
            kp = values['-KP-']
            kd = values['-KD-']
            threading.Thread(target=Controller.send_once,
                             args=(values['-MOTORID-'], position, kp, kd, values['-COM-'],)
                             , daemon=True).start()

        elif event == "STOP":
            threading.Thread(target=Controller.go_to_zero_off, args=(values['-COM-'],), daemon=True).start()

        elif event == "MOTOR STOP":
            threading.Thread(target=Controller.go_to_zero_off, args=(values['-COM-'],),  daemon=True).start()

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
            threading.Thread(target=Controller.run_from_xls, args=(values['-TOUT-'], values['-COM-']),
                             daemon=True).start()

        elif event == "LOOP":
            threading.Thread(target=Controller.run_from_xls_loop, args=(values['-TOUT-'], values['-COM-']),
                             daemon=True).start()


if __name__ == '__main__':
    the_gui()
    print('EXITING PROGRAM')
    time.sleep(0.5)