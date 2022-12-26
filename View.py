from tkinter.font import BOLD
import PySimpleGUI as sg
import os.path
import time
import threading
from Controller import Controller


class View:
    def __init__(self):
        self.controller = Controller()

    def the_gui(self):
        sg.theme('tealmono')

        position_test_demo = [
            [
                sg.Text("Please choose USB port: "),
                sg.Combo(['COM3', 'COM4', 'COM6', 'COM7'], default_value='COM3', size=(10, 1), key='-COM-')

            ],
            [
                sg.Text("Position test controller: ", font=BOLD)
            ],
            [
                sg.Button("MOTORS ON", button_color=('black', 'green')),
                sg.Text("    "),
                sg.Button("MOTORS OFF", button_color=('black', 'red')),
            ],
            [
                sg.Text("Motor ID:"),
                sg.Combo(['1', '2'], default_value='1', key='-MOTORID-'),
                sg.Button("SET ZERO", button_color=('black', 'grey'))
            ],
            [
                sg.Text("Position:"),
                sg.In(size=(5, 1), key="-POSITION-"),
                sg.Text("(-95.5) - 95.5")
            ],
            [
                sg.Text("Kp:        "),
                sg.In(size=(5, 1), key="-KP-"),
                sg.Text("0-500")
            ],
            [
                sg.Text("Kd:        "),
                sg.In(size=(5, 1), key="-KD-"),
                sg.Text("0-5"),
            ],
            [
                sg.Button("SEND ONCE"),
                sg.Text("    "),
                sg.Button("GO TO ZERO", button_color=('black', 'orange'))
            ],
        ]

        file_list_column = [
            [
                sg.Text("Folder:"),
                sg.In(size=(27, 1), enable_events=True, key="-FOLDER-"),
                sg.FolderBrowse(),
            ],
            [
                sg.HSeparator('green', 5)
            ],
            [
                sg.Listbox(
                    values=[], enable_events=True, size=(42, 10), key="-TABLE LIST-"
                )
            ],
        ]
        file_run_section = [
            [
                sg.Text("The file chosen is: "),
                sg.In(size=(28, 1), key="-TOUT-")
            ],
            [
                sg.HSeparator('3')
            ],
            [
                sg.Button("SINGLE RUN"),
                sg.Button("LOOP"),
                sg.Text("Loop count:"),
                sg.Combo(['2', '5', '10', '20', '50', '100', '1000'], default_value='10', key='-LOOP COUNT-'),
                sg.Button("STOP RUN", button_color=('black', 'orange'))
            ],
            [
                sg.HSeparator(3)
            ],
            [
                sg.Button("LOOP DATE&TIME"),
                sg.Button("STOP DATE&TIME LOOP", button_color=('black', 'orange'))
            ],
            [
                sg.Text("Run for X days: "),
                sg.Combo(['1', '2', '3', '4', '5'], default_value='1', key='-RUNNING_DAYS-'),
                sg.Text("Between hours: "),
                sg.Combo(['09:00', '10:00', '11:00', '12:00', '13:00'], default_value='09:00', key='-START_HOUR-'),
                sg.Combo(['12:00', '13:00', '14:00', '15:00', '16:00', '17:00'], default_value='16:00', key='-END_HOUR-'),

            ],
            [
                sg.HSeparator(3)
            ],
            [
                sg.In(size=(21, 1), enable_events=True, key="-INTER FILE-"),
                sg.FileBrowse(),
            ],
            [
                sg.Text("Hit to run interference:"),
                sg.Button('INTERFERE'),
            ],
            [
                sg.HSeparator(3)
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
            ],
            [sg.Output(size=(139, 15))]
        ]

        window = sg.Window('AK 60 Duo Controller', layout)

        while True:
            event, values = window.read()

            if event == "EXIT" or event == sg.WIN_CLOSED:
                self.controller.set_position_zero(values['-COM-'])
                self.controller.motors_off(values['-COM-'])
                break

            elif event == "MOTORS ON":
                threading.Thread(target=self.controller.motors_on, args=(values['-COM-'],), daemon=True).start()

            elif event == "MOTORS OFF":
                threading.Thread(target=self.controller.motors_off, args=(values['-COM-'],), daemon=True).start()

            elif event == "GO TO ZERO":
                threading.Thread(target=self.controller.set_position_zero, args=(values['-COM-'],), daemon=True).start()

            elif event == "STOP RUN":
                threading.Thread(target=self.controller.stop_run, args=(values['-COM-'],), daemon=True).start()

            elif event == "-FOLDER-":
                folder = values["-FOLDER-"]
                try:
                    file_list = os.listdir(folder)
                except:
                    file_list = []

                f_names = [
                    f
                    for f in file_list
                    if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(".xlsx")
                ]
                window["-TABLE LIST-"].update(f_names)

            elif event == "-TABLE LIST-":
                try:
                    filename = os.path.join(
                        values["-FOLDER-"], values["-TABLE LIST-"][0]
                    )
                    window["-TOUT-"].update(filename)
                except:
                    pass

            elif event == "-INTER FILE-":
                try:
                    filename = values["-INTER FILE-"]
                    window["-INTER FILE-"].update(filename)
                except:
                    pass

            elif event == "SINGLE RUN":
                threading.Thread(target=self.controller.run_from_xls,
                                 args=(values['-TOUT-'], values['-COM-'],), daemon=True).start()

            elif event == "SEND ONCE":
                position = values['-POSITION-']
                kp = values['-KP-']
                kd = values['-KD-']
                threading.Thread(target=self.controller.send_once,
                                 args=(values['-MOTORID-'], position, kp, kd, values['-COM-'],),
                                 daemon=True).start()

            elif event == "LOOP":
                threading.Thread(target=self.controller.run_from_xls_loop,
                                 args=(values['-TOUT-'], values['-COM-'], values['-LOOP COUNT-']), daemon=True).start()

            elif event == "LOOP DATE&TIME":
                threading.Thread(target=self.controller.run_from_xls_loop_date,
                                 args=(values['-TOUT-'], values['-COM-'], values['-RUNNING_DAYS-'],
                                       values['-START_HOUR-'], values['-END_HOUR-']), daemon=True).start()

            elif event == "STOP DATE&TIME LOOP":
                self.controller.stop_date_loop(values['-COM-'])

            elif event == "SET ZERO":
                self.controller.zero_position(values['-COM-'])

            elif event == "INTERFERE":
                threading.Thread(target=self.controller.interfere,
                                 args=(values['-TOUT-'],values['-COM-'], values['-LOOP COUNT-'],
                                       values['-INTER FILE-']), daemon=True).start()


if __name__ == '__main__':
    view = View()
    view.the_gui()
    print('EXITING PROGRAM')
    time.sleep(0.5)
