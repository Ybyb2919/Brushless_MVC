from tkinter.font import BOLD
import PySimpleGUI as sg
import os.path
import datetime, time
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
            sg.Button("ON & RUN"),
            sg.Button("LOOP"),
            sg.Button("LOOP DATE&TIME"),
            sg.Button("MOTOR STOP")
        ],
        [
            sg.HSeparator()
        ],
        [
            sg.Text("Loop count:"),
            sg.Combo(['10', '20', '50', '100'], default_value='10', key='-LOOP_COUNT-')
        ],
        [
            sg.Text("Run for X days: "),
            sg.Combo(['1', '2', '3', '4', '5'], default_value='1', key='-RUNNING_DAYS-'),
            sg.Text("Between hours: "),
            sg.Combo(['9:00', '10:00', '11:00', '12:00'], default_value='9:00', key='-START_HOUR-'),
            sg.Combo(['13:00', '14:00', '15:00', '16:00'], default_value='16:00', key='-END_HOUR-'),

        ],
        [
            sg.Text("Hit EXIT to terminate the program:"),
            sg.Button('EXIT', font='Helvetica 12 bold italic', button_color=('black', 'red'), border_width=0, ),
        ],
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

        elif event == "ON & RUN":
            threading.Thread(target=Controller.run_from_xls,
                             args=(values['-TOUT-'], values['-COM-'],), daemon=True).start()

        elif event == "SEND ONCE":
            position = values['-POSITION-']
            kp = values['-KP-']
            kd = values['-KD-']
            threading.Thread(target=Controller.send_once,
                             args=(values['-MOTORID-'], position, kp, kd, values['-COM-'],),
                             daemon=True).start()

        elif event == "LOOP":
            threading.Thread(target=Controller.run_from_xls_loop,
                             args=(values['-TOUT-'], values['-COM-'], values['-LOOP_COUNT-']), daemon=True).start()

        elif event == "LOOP DATE&TIME":
            threading.Thread(target=Controller.run_from_xls_loop_date_time,
                             args=(values['-TOUT-'], values['-COM-'], values['-RUNNING_DAYS-'],
                                   values['-START_HOUR-'], values['-END_HOUR-']), daemon=True).start()

if __name__ == '__main__':
    the_gui()
    print('EXITING PROGRAM')
    time.sleep(0.5)
