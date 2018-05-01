from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt,QEvent
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRect
from helper.serial_scanner import SerialScan
from manage.manager import PlotManager
import pyqtgraph as pg
import serial


class GraphUI(QDialog):
    def __init__(self, width):
        self.plot = None
        self.w = width

    def addgraph(self,funcName):
        # Plot Widget config
        self.plot = pg.PlotWidget(parent=None, background=pg.mkColor('#FFF'))
        self.plot.setLabel('top',funcName)

        self.plot.setAntialiasing(True)
        self.plot.setMinimumWidth(self.w-50)
        self.plot.plotItem.showGrid(True, True, 1)

        return self.plot

    def make_connection(self, _object_):
        # _object_.add_button.connect(self.display)
        _object_.closing.connect(self.clean_up)
        _object_.rescale.connect(self.plot_resize)



