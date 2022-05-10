class Controller:

    def run_from_xls_local(file_name, COM_insert):
        print("Running from" + file_name)
        try:
            run_from_xls(file_name, COM_insert)
        except:
            print("Cannont run sequence from .xls file")
            pass

    def run_from_xls_loop(file_name, COM_insert):
        print("Looping from : " + file_name)
        run_from_xls_loop(file_name, COM_insert)

    def turn_on(COM_insert):
        try:
            with Motor.connect(COM_insert) as motor:
                motor.init(1)
                time.sleep(1)
                motor.init(2)
        except:
            print("Cannont Turn on motors")
            print("Please initially run motors using an excel file (temporary)")
            pass

    def read_position_local(COM_insert):
        try:
            with Motor.connect(COM_insert) as motor:
                return motor.read_position()
        except:
            print("Cannot read position")
            pass