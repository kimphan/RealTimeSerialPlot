
"""
Real-Time Graph: local process
    Role: data computation for Sine Wave graph
    References:
        https://docs.python.org/2/library/multiprocessing.html
    Credit for:
        https://github.com/ssepulveda/RTGraph
"""
import platform, glob
import multiprocessing as mp
import serial
from helper.serial_scanner import SerialScan
from time import time
import glob, platform, serial
from serial.tools import list_ports


class SerialStream(mp.Process):

    # Constructor
    def __init__(self, prser):
        mp.Process.__init__(self)
        self._parser = prser
        self._exit = mp.Event()
        self._serial = serial.Serial()
        self._scan = SerialScan()
        self.port_available = self._scan.scan_serial_port()

    def _is_ports_available(self, port):
        for p in self.port_available:
            if port == p:
                return True
        return False

    def run(self):
        if not self._serial.is_open:
            try:
                self._serial.open()
                self.readStream()
            except serial.SerialException:
                print('Cannot open port')
                self._serial.close()
        else:
            self.readStream()


    def check_init(self, port=None, speed=115200):
        if self.name is not None:
            self._serial.port = port
            self._serial.baudrate = speed
            self._serial.stopbits = serial.STOPBITS_ONE
            self._serial.bytesize = serial.EIGHTBITS
            self._serial.timeout = 1
            return True
        else:
            return False

    def stop(self):
        print('serial stop')
        self._exit.set()

    def readStream(self):
        t = time()
        while not self._exit.is_set():
            line = self._serial.readline()
            self._parser.add([time()-t, line])
        self._serial.close()

    # @staticmethod
    # def get_os_type():
    #     os_name = platform.platform()
    #     if 'Darwin' in os_name:
    #         os_type = 0
    #     elif 'Window' in os_name:
    #         os_type = 1
    #     elif 'Linux' in os_name:
    #         os_type = 2
    #     else:
    #         os_type = 4
    #     return os_type
    #
    # # Scan available serial port
    # def scan_serial_port(self, os):
    #     ports_available = []
    #     if os == 0:
    #         return glob.glob('/dev/tty.*')
    #     else:
    #         for p in list(list_ports.comports()):
    #             ports_available.append(p.device)
    #         return ports_available



