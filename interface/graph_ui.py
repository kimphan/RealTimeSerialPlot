from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt,QEvent
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRect
from helper.serial_scanner import SerialScan
from manage.manager import PlotManager
import pyqtgraph as pg
import serial


class GraphUi(QDialog):
    rm_action = pyqtSignal(int)
    plot_action = pyqtSignal(int)
    stop_action = pyqtSignal(int)
    subplot_draw = pyqtSignal(str,int, int,int)

    def __init__(self, graph_i=0, width=900, height=300, xn=None, yn=None, title=None, key=0):
        super(GraphUi,self).__init__()
        self.scan = SerialScan()
        self.list_ports = self.scan._scan_serial_port()
        self.add = 0
        self.graphID = graph_i
        self.width = width
        self.height = height
        self.xname = xn
        self.yname = yn
        self.graphName = title
        self.key = key
        self.control_panel = QFormLayout()
        self.plot = None
        self.sample_num = None
        self.rate_num = None
        self.serial_port = None
        self.run_btn = None
        self.stop_btn = None
        self.remove_btn = None
        self.clist = None
        self.plot_manager = None


    def addgraph(self):
        # Setup widget
        self._widget_config()

        # Qt Display
        layout = QHBoxLayout()
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.run_btn)

        graph_widget = QGroupBox(self.graphName)
        graph_widget.setObjectName(str(self.key))
        graph_widget.setStyleSheet('font-size: 12pt; font-style: bold; color: 606060;')
        graph_widget.setFixedHeight(self.height)
        graph_widget.setFixedWidth(self.width)

        graph_layout = QGridLayout()

        sub_widget = QWidget()
        self.control_panel = QFormLayout()
        self.control_panel.setAlignment(Qt.AlignRight)
        self.control_panel.addRow(str('Sample: '), self.sample_num)
        if self.graphID==0:
            self.rate_num.setText('115200')
            self.control_panel.addRow(str('Baudrate: '), self.rate_num)
            self.control_panel.addRow(str('Port: '), self.serial_port)
            self.control_panel.addRow(str('Channel: '), self.clist)
        else:
            self.control_panel.addRow(str('Rate: '), self.rate_num)
            if self.graphID==1:
                self.control_panel.addRow(str('Channel: '), self.clist)

        self.control_panel.addRow(str(''),layout)
        self.control_panel.addRow(str(''),self.remove_btn)

        sub_widget.setLayout(self.control_panel)

        graph_layout.addWidget(self.plot, 0, 0, 3, 1, Qt.AlignLeft)
        graph_layout.addWidget(sub_widget, 0, 1, 3, 1,Qt.AlignLeft)

        graph_widget.setLayout(graph_layout)

        self.enable_ui(True,self.stop_btn, self.run_btn, self.rate_num, self.serial_port)
        return graph_widget


    def _widget_config(self):
        # Plot Widget config
        self.plot = pg.PlotWidget(parent=None, background=pg.mkColor('#FFF'))
        self.plot.setLabel('left', self.yname)
        self.plot.setLabel('bottom', self.xname)
        self.plot.setAntialiasing(True)
        self.plot.setMinimumWidth(self.width*3/4)
        self.plot.plotItem.showGrid(True, True, 1)

        # Other setup config
        self.sample_num = QLineEdit()
        self.sample_num.setText('100')
        self.rate_num = QLineEdit()
        self.rate_num.setText('0.02')

        self.serial_port = QComboBox()
        self.serial_port.setEditable(True)
        self.serial_port.setFixedWidth(100)
        for o in self.list_ports:
            self.serial_port.addItem(o)

        self.clist = QComboBox()
        self.clist.setEditable(True)
        self.clist.currentIndexChanged.connect(self.selectionChange)

        self.run_btn = QPushButton('Run')
        self.run_btn.setObjectName(str(self.key))
        self.run_btn.setStyleSheet('font-size: 12pt;')

        self.stop_btn = QPushButton('Stop')
        self.stop_btn.setObjectName(str(self.key))
        self.stop_btn.setStyleSheet('font-size: 12pt;')

        self.remove_btn = QPushButton('Remove')
        self.remove_btn.setObjectName(str(self.key))
        self.remove_btn.setStyleSheet('font-size: 12pt;')

        self.remove_btn.pressed.connect(self.on_remove_event)
        self.run_btn.pressed.connect(self.on_run_event)
        self.stop_btn.pressed.connect(self.on_stop_event)

    def make_connection(self, _object_):
        # _object_.add_button.connect(self.display)
        _object_.closing.connect(self.clean_up)
        _object_.rescale.connect(self.plot_resize)

    # Remove button Handler
    def on_remove_event(self):
        remove_id = int(self.sender().objectName())
        self.rm_action.emit(remove_id)

    # Run button Handler
    def on_run_event(self):
        self.enable_ui(False,self.stop_btn, self.run_btn, self.rate_num, self.serial_port)
        run_id = int(self.sender().objectName())
        self.plot_action.emit(run_id)

    def on_stop_event(self):
        self.enable_ui(True,self.stop_btn, self.run_btn, self.rate_num, self.serial_port)
        stop_id = int(self.sender().objectName())
        self.stop_action.emit(stop_id)

    def enable_ui(self, e, stop_btn, run_btn, rate_num, serial_port):
        rate_num.setEnabled(e)
        serial_port.setEnabled(e)
        run_btn.setEnabled(e)
        stop_btn.setEnabled(not e)

    def channel_scan(self):
        if self.graphID==1:
            c = 2
        elif self.graphID == 0:
            for p in self.list_ports:
                try:
                    ser = serial.Serial(port=p,baudrate=115200,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
                    if ser.is_open:
                        line = ser.readline()
                    values = line.decode("UTF-8").split(',')
                    c = len(values)
                    self.serial_port.setCurrentText(p)
                    ser.close()
                except:
                    print('Access denied')
        else: c = -1
        if c > 1:
            self.clist.addItem('Both')
            for i in range(c):
                self.clist.addItem('Channel '+str(i+1))

    def selectionChange(self,i):
        if i > 0:
            # Draw the child graph
            self.subplot_draw.emit(self.clist.currentText(),self.key,self.graphID,i)


