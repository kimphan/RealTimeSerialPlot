from PyQt5.QtWidgets import *
import pyqtgraph as pg


class GraphUI(QDialog):
    def __init__(self, width, height):
        self.plot = None
        self.w = width
        self.h = height

    def addgraph(self,funcName):
        # Plot Widget config
        self.plot = pg.PlotWidget(parent=None, background=pg.mkColor('#FFF'))
        self.plot.setLabel('top',funcName)
        self.plot.setAntialiasing(True)
        self.plot.plotItem.showGrid(True, True, 1)
        self.plot.setMinimumWidth(self.w-100)
        self.plot.setMaximumHeight(self.h)
        return self.plot
    def make_connection(self, _object_):
        # _object_.add_button.connect(self.display)
        _object_.closing.connect(self.clean_up)
        _object_.rescale.connect(self.plot_resize)



