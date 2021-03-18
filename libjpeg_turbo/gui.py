from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sender
import serverui as ui


class Main(QMainWindow, ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.Start_Button.clicked.connect(self.start_button_clicked)
        self.Stop_Button.clicked.connect(self.stop_button_clicked)
        self.server = sender.StartServer()
        self.server_thread = None
        self.cli_addr = []
        self.ip = []
        self.iptool = IpService(self.ip, self)
        self.iptool.start()
        self.iptool.finished.connect(self.show_my_ip)

    def start_button_clicked(self):
        self.logs.appendPlainText('start server.\nwaiting for request...')
        self.server.start()
        self.server_thread = ServerService(self.cli_addr, self.server, self)
        self.server_thread.start()
        self.server_thread.finished.connect(self.client_connected)
        self.Start_Button.setEnabled(False)
        self.Stop_Button.setEnabled(True)

    def client_connected(self):
        self.logs.appendPlainText(f'client ip:{self.cli_addr[0]} connected')

    def stop_button_clicked(self):
        self.logs.appendPlainText('stop server')
        self.server.stop()
        self.logs.appendPlainText('server has stopped.')
        self.Start_Button.setEnabled(True)
        self.Stop_Button.setEnabled(False)

    def show_my_ip(self):
        self.logs.appendPlainText(f'server ip:{self.ip[0]}')


class ServerService(QThread):
    def __init__(self, ret: list, server, parent=None):
        QThread.__init__(self, parent=parent)
        self.server = sender.StartServer()
        self.client_addr = None
        self.server = server
        self.ret = ret

    def run(self):
        while self.client_addr is None:
            self.client_addr = self.server.get_addr()
        self.ret.append(self.client_addr)


class IpService(QThread):
    def __init__(self, ret: list, parent=None):
        QThread.__init__(self, parent=parent)
        self.ret = ret
        self.sock = None
        self.ip = None

    def run(self):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        self.ret.append(ip)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
