from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from interface.graph_ui import GraphUI
from interface.log_ui import LogUI
from manage.manager import PlotManager
from helper.serial_scanner import SerialScan


class MainWindow(QMainWindow):
    LABELFONT = 15

    def __init__(self):
        super(MainWindow, self).__init__()
        self.w = 1400
        self.h = 800
        self.setMinimumHeight(self.h)
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
        self.portAvailable = False
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

        self.log_dialog = LogUI()


    # Setup UI for main window
    def loadui(self):
        # Widgets
        self.ports_list = QComboBox()
        self.ports_list.currentTextChanged.connect(self.selection_change)
        self.baudrate = QLineEdit()
        self.baudrate.setText('115200')
        self.samples = QLineEdit()
        self.samples.setText('100')
        self.samples.setEnabled(True)
        self.samples.keyPressEvent = self.keyPressEvent
        self.scan_btn = self.button('Scan Port',self.get_available_port)
        self.run_btn = self.button('Run',self.run_plot)
        self.stop_btn = self.button('Stop',self.stop_plot)
        self.log_checkbox = QCheckBox('Log')
        self.log_checkbox.stateChanged.connect(self.log_state)

        sample_layout = QHBoxLayout()
        sample_layout.addWidget(self.samples)
        sample_layout.addWidget(self.log_checkbox)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.stop_btn)
        buttonLayout.addWidget(self.run_btn)

        vertical_menu = QVBoxLayout()
        vertical_menu.setAlignment(Qt.AlignLeft)
        vertical_menu.SetFixedSize

        # Serial Setup Box
        serial_box = QGroupBox('Serial Setup')
        serial_box.setStyleSheet('font-size: 12pt; color: 606060;')
        serial_form = QFormLayout()
        serial_form.addRow('Port',self.ports_list)
        serial_form.addRow('Baudrate',self.baudrate)
        serial_form.addRow('', self.scan_btn)
        serial_box.setLayout(serial_form)
        serial_box.setFixedWidth(self.w/6)
        serial_box.setFixedHeight(self.h/6)

        # Function Box
        func1 = QCheckBox('Raw Data')
        func1.setObjectName('Raw Data')
        self.funcList.append(func1)

        func2 = QCheckBox('Autocorrelation')
        func2.setObjectName('Autocorrelation')
        self.funcList.append(func2)

        func3 = QCheckBox('Heart Beat')
        func3.setObjectName('Heart Beat')
        self.funcList.append(func3)

        function_box = QGroupBox('Function')
        function_box.setStyleSheet('font-size: 12pt; color: 606060;')
        function_form = QFormLayout()
        function_form.addRow('Samples: ',sample_layout)

        for f in self.funcList:
            function_form.addRow(f)
            f.stateChanged.connect(self.function_selection)

        function_form.addRow('',buttonLayout)
        function_box.setLayout(function_form)
        function_box.setFixedWidth(self.w/6)
        function_box.setMaximumHeight(self.h*4/6)

        # Channel Box
        channel_box = QGroupBox('Channel List')
        channel_box.setStyleSheet('font-size: 12pt; color: 606060;')
        self.channel = QFormLayout()
        channel_box.setLayout(self.channel)
        channel_box.setFixedWidth(self.w/6)


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
        stat_box.setFixedWidth(self.w/6)
        stat_box.setFixedHeight(self.h)

        statistic.addWidget(stat_box)

        self.windowLayout.addLayout(vertical_menu)
        self.windowLayout.addStretch(1)
        self.windowLayout.addLayout(self.graph_display)
        self.windowLayout.addStretch(1)
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
    def selection_change(self, currport):
        if self.clist:
            self.clear_clist()
        self.pmanager.setup_serial(self.samples.text(), self.baudrate.text(),currport)
        if not self.scan.open_port(currport,self.baudrate.text()):
            self.run_btn.setEnabled(False)
            self.log_checkbox.setCheckable(False)
            self.portAvailable = False
        else:
            line = self.scan.line
            if line != 0:
                self.portAvailable = True
                self.run_btn.setEnabled(True)
                self.log_checkbox.setCheckable(True)
                # List all the channels read from serial port
                for c in range(line):
                    entry = QCheckBox('Channel '+str(c))
                    entry.setObjectName(str(c))
                    entry.setChecked(True)
                    entry.stateChanged.connect(self.channel_display)
                    self.clist.append(entry)
                    self.channel.addRow(entry)
                    self.pmanager.add_channel(c)
            else:
                self.portAvailable = False
                self.run_btn.setEnabled(False)
                self.log_checkbox.setCheckable(False)
            self.isClicked = False

    def stop_plot(self):
        if self.pmanager.is_running():
            self.pmanager.stop()
        self.log_checkbox.setEnabled(True)

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
        if self.portAvailable:
            if not self.pmanager.is_running():
                self.pmanager.start()
        else:
            self.alert('Port is Not available! Please choose another port.')

    def function_selection(self):
        for f in self.funcList:
            funcname = f.objectName()
            if f.isChecked() and funcname not in self.plotDictionary.keys():
                plot_widget = GraphUI(self.w*5/7,self.h/3).addgraph(funcname)
                self.graph_display.addWidget(plot_widget,self.plot_count, 0, Qt.AlignLeft)
                self.plotDictionary.update({funcname: plot_widget})
                self.pmanager.update_plotDict(self.plotDictionary)
                self.plot_count +=1
            elif not f.isChecked() and funcname in self.plotDictionary.keys():
                self.graph_display.removeWidget(self.plotDictionary[funcname])
                self.plotDictionary[funcname].deleteLater()
                del self.plotDictionary[funcname]
                self.pmanager.update_plotDict(self.plotDictionary)

    def channel_display(self):
        if self.clist:
            for c in self.clist:
                if c.isChecked():
                    self.pmanager.add_channel(int(c.objectName()))
                else:
                    self.pmanager.remove_channel(int(c.objectName()))

    def log_state(self):
        if self.log_checkbox.isChecked():
            self.statusBar().showMessage('Log Enable')
            self.log_dialog.showdialog()
            self.log_dialog.log_signal.connect(self.start_log)
        else:
            self.statusBar().showMessage('Log Disable')
            self.log_dialog.cancel()

    @pyqtSlot(bool,str)
    def start_log(self,file_ready,filename):
        self.pmanager.csv_checked(file_ready,filename)

    # User's event handler
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.pmanager.update_samples(self.new_samples)
            self.new_samples = ''
        elif event.key() == Qt.Key_Backspace:
            self.samples.setText('')
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
                self.h = 800
                self.w = 1400
                self.resize_plot(self.w*5/7-100,self.h/3)
        super(MainWindow,self).changeEvent(event)

    def resize_plot(self,w,h):
        for k in self.plotDictionary.keys():
            self.plotDictionary[k].setMinimumWidth(w)
            self.plotDictionary[k].setMaximumHeight(h)
