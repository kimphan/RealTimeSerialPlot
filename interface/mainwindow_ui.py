from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from interface.graph_ui import GraphUI
from manage.manager import PlotManager
from helper.serial_scanner import SerialScan
from processes.serial import SerialStream
from functools import partial
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
        self.new_samples = ''
        self.addtopbottom = False
        self.scan = SerialScan()
        self.clist = [] # Channel list
        self.funcList = []  # Function list
        self.plotDictionary = dict() # Plot widget

        self.pmanager = PlotManager()

        self.store_graph = dict()
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
        self.ports_list.currentTextChanged.connect(self.selectionChange)
        self.baudrate = QLineEdit()
        self.baudrate.setText('115200')
        self.samples = QLineEdit()
        self.samples.setText('100')
        self.samples.setEnabled(True)
        self.samples.keyPressEvent = self.keyPressEvent
        self.scan_btn = self.button('Scan Port',self.get_available_port)
        self.run_btn = self.button('Run',self.run_plot)
        self.stop_btn = self.button('Stop',self.serial_stop)


        vertical_menu = QVBoxLayout()
        vertical_menu.setAlignment(Qt.AlignLeft)
        vertical_menu.SetFixedSize

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.stop_btn)
        buttonLayout.addWidget(self.run_btn)

        # Serial Setup Box
        serial_box = QGroupBox('Serial Setup')
        serial_box.setStyleSheet('font-size: 12pt; color: 606060;')
        serial_form = QFormLayout()
        serial_form.addRow('Port',self.ports_list)
        serial_form.addRow('Baudrate',self.baudrate)
        serial_form.addRow('', self.scan_btn)
        serial_box.setLayout(serial_form)
        serial_box.setFixedWidth(self.w/7)
        serial_box.setFixedHeight(self.h/4)

        # Function Box
        func1 = QCheckBox('Raw Data')
        func1.setObjectName('Raw Data')
        func2 = QCheckBox('Autocorrelation')
        func2.setObjectName('Autocorrelation')
        func3 = QCheckBox('Heart Beat')
        func3.setObjectName('Heart Beat')
        self.funcList.append(func1)
        self.funcList.append(func2)
        self.funcList.append(func3)

        function_box = QGroupBox('Function')
        function_box.setStyleSheet('font-size: 12pt; color: 606060;')
        function_form = QFormLayout()
        function_form.addRow('Samples ',self.samples)
        for f in self.funcList:
            function_form.addRow(f)
            f.stateChanged.connect(self.function_selection)

        function_form.addRow(self.stop_btn,self.run_btn)
        function_box.setLayout(function_form)
        function_box.setFixedWidth(self.w/7)
        function_box.setFixedHeight(self.h*2/4)

        # Channel Box
        channel_box = QGroupBox('Channel List')
        channel_box.setStyleSheet('font-size: 12pt; color: 606060;')
        self.channel = QFormLayout()
        channel_box.setLayout(self.channel)
        channel_box.setFixedWidth(self.w/7)
        channel_box.setFixedHeight(self.h/4)


        vertical_menu.addWidget(serial_box)
        vertical_menu.addWidget(function_box)
        vertical_menu.addWidget(channel_box)

        # Display box
        self.graph_display = QGridLayout()
        self.graph_display.setAlignment(Qt.AlignTop)
        self.graph_display.SetFixedSize

        # Legend box
        self.breathPeriod = QLabel('0')
        self.respRate = QLabel('0')
        self.respRate_variability = QLabel('0')
        self.sleepStage = QLabel('0')

        statistic = QVBoxLayout()
        statistic.setAlignment(Qt.AlignRight)
        statistic.SetFixedSize

        stat_box = QGroupBox('Legend')
        stat_box.setStyleSheet('font-size: 12pt; color: 606060;')
        stat_form = QFormLayout()
        stat_form.addRow('Breathing Period: ', self.breathPeriod)
        stat_form.addRow('Respiration Rate (RR): ', self.respRate)
        stat_form.addRow('RR Variability: ', self.respRate_variability)
        stat_form.addRow('Sleep Stage: ', self.sleepStage)
        stat_box.setLayout(stat_form)
        stat_box.setFixedWidth(self.w/7+50)
        stat_box.setFixedHeight(self.h)

        statistic.addWidget(stat_box)

        self.windowLayout.addLayout(vertical_menu)
        self.windowLayout.addLayout(self.graph_display)
        self.windowLayout.addStretch()

        self.windowLayout.addLayout(statistic)

        # Get all the serial port available
        for prt in self.pmanager.get_port():
            self.ports_list.addItem(prt)

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

    # List the channels read from serial port
    def selectionChange(self, currPort):
        if self.clist:
            self.clear_clist()
        self.pmanager.setup_serial(self.samples.text(),self.baudrate.text(),currPort)
        if not self.scan.open_port(currPort,self.baudrate.text()):
            # self.alert('Cannot find a serial port!')
            pass
        else:
            line = self.scan.line
            if line != 0:
                # List all the channels read from serial port
                for c in range(line):
                    entry = QCheckBox('Channel '+str(c))
                    entry.setObjectName(str(c))
                    entry.setChecked(True)
                    entry.stateChanged.connect(self.channel_display)
                    self.clist.append(entry)
                    self.channel.addRow(entry)
                    self.pmanager.add_channel(c)
            self.isClicked = False


    def serial_stop(self):
        if self.pmanager.is_running():
            self.pmanager.stop()
        print('Stop serial port.')

    def clear_clist(self):
        row_count = self.channel.rowCount()
        self.isReady = False
        self.scan.line = 0
        self.clist.clear()
        while row_count >= 0:
            self.channel.removeRow(row_count)
            row_count -= 1

    def run_plot(self):
        # Start plotting
        if not self.pmanager.is_running():
            self.pmanager.start()

    def function_selection(self):
        for f in self.funcList:
            funcName = f.objectName()
            if f.isChecked() and funcName not in self.plotDictionary.keys():
                plot_widget = GraphUI(self.w*5/7,self.h/3).addgraph(funcName)
                self.graph_display.addWidget(plot_widget,self.plot_count, 0, Qt.AlignLeft)
                self.plotDictionary.update({funcName: plot_widget})
                self.pmanager.update_plotDict(self.plotDictionary)
                self.plot_count +=1
            elif not f.isChecked() and funcName in self.plotDictionary.keys():
                self.graph_display.removeWidget(self.plotDictionary[funcName])
                self.plotDictionary[funcName].deleteLater()
                del self.plotDictionary[funcName]
                self.pmanager.update_plotDict(self.plotDictionary)

    def channel_display(self):
        if self.clist:
            for c in self.clist:
                if c.isChecked():
                    self.pmanager.add_channel(int(c.objectName()))
                else:
                    self.pmanager.remove_channel(int(c.objectName()))

    def save_data(self):
        pass

    # User's event handler
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.pmanager.update_samples(self.new_samples)
            self.new_samples = ''
        elif event.key() == Qt.Key_Backspace:
            self.samples.clear()
        else:
            if event.text().isdigit():
                self.new_samples += event.text()
                self.samples.setText(self.new_samples)

    def closeEvent(self, event):
        if self.pmanager.is_running():
            self.pmanager.stop()
        super(MainWindow, self).closeEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            # if self.windowState() == Qt.WindowFullScreen:
            if self.windowState() & Qt.WindowMaximized:
                screen_resolution = qApp.desktop().screenGeometry()
                self.w, self.h = screen_resolution.width(), screen_resolution.height()
                self.resize_plot(self.w*5/7-100,self.h/3)
            else:
                self.h = 700
                self.w = 1300
                self.resize_plot(self.w*5/7-100,self.h/3)

        super(MainWindow,self).changeEvent(event)

    def resize_plot(self,w,h):
        for k in self.plotDictionary.keys():
            self.plotDictionary[k].setFixedWidth(w)
            self.plotDictionary[k].setFixedHeight(h)
