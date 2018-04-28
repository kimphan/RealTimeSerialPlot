
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


class Serial(mp.Process):

    # Constructor
    def __init__(self, prser):
        mp.Process.__init__(self)
        self._parser = prser
        self._exit = mp.Event()
        self._serial = serial.Serial()
        self._os = SerialScan()

    def _is_ports_available(self, port):
        for p in self._os._scan_serial_port():
            if port == p:
                return True
        return False

    def run(self):
        if self._is_ports_available(self._serial.port):
            if not self._serial.is_open:
                try:
                    self._serial.open()
                    self.readStream()
                except serial.SerialException:
                    print('Cannot open port')
                    self._serial.close()
            else:
                self.readStream()
        else:
            print('Port is not available.')

    def check_init(self, port=None, speed=115200):
        if self.name is not None:
            self._serial.port = port
            self._serial.baudrate = int(speed)
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





