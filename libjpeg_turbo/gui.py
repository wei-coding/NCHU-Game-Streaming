from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sender
import socket
import serverui as ui


class Main(QMainWindow, ui.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.Start_Button.clicked.connect(self.start_button_clicked)
        self.Stop_Button.clicked.connect(self.stop_button_clicked)
        self.loadthread = None
        self.cli_addr = []

    def start_button_clicked(self):
        self.logs.appendPlainText('start server.\nwaiting for request...')
        self.loadthread = Worker(self.cli_addr, self)
        self.loadthread.start()
        self.loadthread.finished.connect(self.client_connected)
        self.Start_Button.setEnabled(False)

    def client_connected(self):
        self.logs.appendPlainText(f'client[{self.cli_addr[0]}] connected')

    def stop_button_clicked(self):
        self.logs.appendPlainText('stop server')


class Worker(QThread):

    def __init__(self,  ret: list, parent=None):
        QThread.__init__(self, parent=parent)
        self.server = sender.StartServer()
        self.client_addr = None
        self.server.start()
        self.ret = ret

    def run(self):
        while self.client_addr is None:
            self.client_addr = self.server.get_addr()
        self.ret.append(self.client_addr)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
