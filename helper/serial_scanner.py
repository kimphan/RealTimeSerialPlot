import glob, platform, serial
from serial.tools import list_ports
class SerialScan:

    def __init__(self):
        self._os = SerialScan._get_os_name()
        self.line = 0

    @staticmethod
    def _get_os_name():
        os_name = platform.platform()
        if 'Darwin' in os_name:
            os_type = 0
        elif 'Window' in os_name:
            os_type = 1
        elif 'Linux' in os_name:
            os_type = 2
        else:
            os_type = 4

    # Scan available serial port
    def scan_serial_port(self):
        ports_available = []
        if self._os == 0:
            return glob.glob('/dev/tty.*')
        else:
            for p in list(list_ports.comports()):
                ports_available.append(p.device)
            return ports_available

    def open_port(self, port, brate):
        try:
            ser = serial.Serial(port=port,baudrate=int(brate),stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
            if not ser.is_open:
                ser.open()
            else:
                line = ser.readline()
                values = line.decode("UTF-8").split(',')
                for v in values:
                    if v != '':
                        self.line += 1
            ser.close()
        except:
            return False
        return True

