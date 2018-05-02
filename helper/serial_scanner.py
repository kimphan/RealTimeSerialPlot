import glob, platform, serial
from serial.tools import list_ports
class SerialScan:

    def __init__(self):
        self.line = 0
        self.ser = None

    def open_port(self, port, brate):
        try:
            self.ser = serial.Serial(port=port,baudrate=int(brate),stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
            if not self.ser.is_open:
                self.ser.open()
            else:
                line = self.ser.readline()
                values = line.decode("UTF-8").split(',')
                for v in values:
                    if v != '':
                        self.line += 1
                self.ser.close()
        except:
            return False
        return True

