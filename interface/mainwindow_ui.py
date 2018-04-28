from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, pyqtSlot
from interface.graph_ui import GraphUi
from manage.manager import PlotManager
from helper.serial_scanner import SerialScan
import os, signal,serial


class MainWindow(QMainWindow):
    LABELFONT = 15
    add_button = pyqtSignal('QGridLayout', int, int, int, str, str, str, int)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.w = 1300
        self.h = 700
        self.setMinimumHeight(self.h+100)
        self.setMinimumWidth(self.w)
        self.center()
        self.statusBar().showMessage('Ready')
        self.setWindowTitle('Channel Plot')

        self.key = 0
        self.plot_count = 0
        self.add = 0
        self.splot_count = 0
        self.splot = -1
        self.addtopbottom = False
        self.scan = SerialScan()
        self.clist = []

        self.store_graph = dict()
        self.store_plot = dict()
        self.store_subplot = dict()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.windowLayout = QHBoxLayout()
        self.windowLayout.setAlignment(Qt.AlignLeft)
        self.central_widget.setLayout(self.windowLayout)
        self.loadui()

    # Setup UI for main window
    def loadui(self):
        # Widgets
        self.ports_list = QComboBox()
        self.baudrate = QLineEdit()
        self.baudrate.setText('115200')
        self.start_btn = self.button('Start',self.serial_start)
        self.stop_btn = self.button('Stop',self.serial_stop)

        # Get available serial port
        self.get_available_port()

        vertical_menu = QVBoxLayout()
        vertical_menu.setAlignment(Qt.AlignLeft)
        vertical_menu.SetFixedSize

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.stop_btn)
        buttonLayout.addWidget(self.start_btn)

        # Serial Setup Box
        serial_box = QGroupBox('Serial Setup')
        serial_box.setStyleSheet('font-size: 12pt; color: 606060;')
        serial_form = QFormLayout()
        serial_form.addRow('Port',self.ports_list)
        serial_form.addRow('Baudrate',self.baudrate)
        serial_form.addRow('',buttonLayout)
        serial_box.setLayout(serial_form)
        serial_box.setFixedWidth(self.w/7)
        serial_box.setFixedHeight(self.h/5)
        
        # Channel Box
        channel_box = QGroupBox('Add Channel')
        channel_box.setStyleSheet('font-size: 12pt; color: 606060;')
        self.channel = QFormLayout()
        channel_box.setLayout(self.channel)
        channel_box.setFixedWidth(self.w/7)

        vertical_menu.addWidget(serial_box)
        vertical_menu.addWidget(channel_box)

        # Display box
        self.graph_display = QGridLayout()
        self.graph_display.setAlignment(Qt.AlignTop)
        self.graph_display.SetFixedSize

        self.windowLayout.addLayout(vertical_menu)
        self.windowLayout.addLayout(self.graph_display)
        self.windowLayout.addStretch()

    # Put the application window in the center of the screen
    def center(self):
        frame = self.frameGeometry()  # specifying geometry of the main window with a rectangle 'qr'
        cp = QDesktopWidget().availableGeometry().center()  # screen size resolution+get the center point
        frame.moveCenter(cp)  # set the rectangle center to the center of the screen
        self.move(frame.topLeft())  # move the top-left point of the application window to the 'qr'
        
    # Button and event handling
    def button(self,name, handler, fontsize=12):
        btn = QPushButton(name)
        btn.setStyleSheet('font-size: {}pt;'.format(fontsize))
        btn.pressed.connect(handler)
        return btn

    def alert(self,message):
        m = QMessageBox.information(self, 'Message', message, QMessageBox.Ok)
        if QMessageBox.Ok:
            pass

    def get_available_port(self):
        plist = self.scan.scan_serial_port()
        self.ports_list.clear()
        if len(plist) == 0:
            self.alert('Cannot find the serial port')
        else:
            for p in plist:
                self.ports_list.addItem(p)

    def serial_start(self):
        self.clear_clist()
        if not self.scan.open_port(self.ports_list.currentText(),self.baudrate.text()):
            self.alert('Cannot find a serial port!')
        else:
            line = self.scan.line
            if line == 0:
                self.alert('Access Denied! Cannot read from this port! Please choose another port.')
            else:
                for c in range(line):
                    entry = QCheckBox()
                    entry.setObjectName(str(c))
                    self.clist.append(entry)
                    self.channel.addRow('Channel '+str(c),entry)

    def serial_stop(self):
        print('Stop serial port.')

    def clear_clist(self):
        row_count = self.channel.rowCount()
        self.scan.line = 0
        self.clist.clear()
        while row_count >= 0:
            self.channel.removeRow(row_count)
            row_count -= 1

    def graph(self):
        print('Graph')
