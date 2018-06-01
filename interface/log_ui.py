from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
import csv,os


class LogUI(QDialog):
    log_signal = pyqtSignal(bool,str)
    def __init__(self):
        super(LogUI,self).__init__()
        self.dialog_win = QDialog()
        self.dialog_win.setFixedSize(200,70)
        self.log_btn = QPushButton('Log',self.dialog_win)
        self.log_btn.clicked.connect(self.logging)
        self.cancel_btn = QPushButton('Cancel',self.dialog_win)
        self.cancel_btn.clicked.connect(self.cancel)
        self.file_name = QLineEdit()

    def showdialog(self):
        buttons = QHBoxLayout()
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.log_btn)
        form = QFormLayout()
        form.addRow('File name: ',self.file_name)
        form.addRow('',buttons)
        self.dialog_win.setLayout(form)
        self.dialog_win.setWindowTitle('Log')
        self.dialog_win.show()

    def logging(self):
        if self.file_name.text() == '':
            m = QMessageBox.information(self, 'Message', 'Please enter a file name', QMessageBox.Ok)
            if QMessageBox.Ok:
                pass
        else:
            self.log_signal.emit(True,self.file_name.text())
            self.dialog_win.close()

    def cancel(self):
        self.dialog_win.close()





