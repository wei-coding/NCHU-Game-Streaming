from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sender
import serverui as ui
import webbrowser
import serversig


class Main(QMainWindow, ui.Ui_MainWindow):
    stop_sig = pyqtSignal()
    start_sig = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.start_button.clicked.connect(self.start_button_clicked)
        self.stop_button.clicked.connect(self.stop_button_clicked)
        self.server = None
        self.server_thread = None
        self.cli_addr = []
        self.ip = []
        self.iptool = IpService(self.ip, self)
        self.iptool.start()
        self.iptool.finished.connect(self.show_my_ip)
        self.signal_service = None
        self.stop_sig.connect(self.after_server_stop)
        self.start_sig.connect(self.after_server_start)

        self.write_welcome_message()
        self.about_button.clicked.connect(lambda: webbrowser.open('https://github.com/wei-coding/Game-Streaming-Nchu'))

    def start_button_clicked(self):
        self.logs.appendPlainText('start server.\nwaiting for connection.')
        port = self.port_textedit.toPlainText()
        if port == '':
            self.server = sender.StartServer(parent=self)
            self.signal_service = KeyboardMouse(parent=self)
        else:
            self.server = sender.StartServer(int(port), self)
            self.signal_service = KeyboardMouse(int(port)+1, parent=self)
        self.server_thread = ServerService(self.cli_addr, self.server, self)
        self.server_thread.start()
        self.server_thread.finished.connect(self.client_connected)
        self.signal_service.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def after_server_start(self):
        self.logs.appendPlainText('server has started.')
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.port_textedit.setEnabled(False)

    def client_connected(self):
        self.logs.appendPlainText(f'client ip: {self.cli_addr[0]} connected')

    def stop_button_clicked(self):
        self.logs.appendPlainText('stop server')
        self.server_thread.stop()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def show_my_ip(self):
        self.logs.appendPlainText(f'server ip: {self.ip[0]}')

    def after_server_stop(self):
        self.logs.appendPlainText('server has stopped.')
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.port_textedit.setEnabled(True)

    def write_welcome_message(self):
        self.logs.appendPlainText('Welcome to GameStreaming Server!')


class ServerService(QThread):
    def __init__(self, ret: list, server, parent=None):
        QThread.__init__(self, parent=parent)
        self.server = server
        self.client_addr = None
        self.server = server
        self.server.start()
        self.ret = ret

    def run(self):
        while self.client_addr is None:
            self.client_addr = self.server.get_addr()
        self.ret.append(self.client_addr)

    def stop(self):
        self.server.stop()


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


class KeyboardMouse(QThread):
    def __init__(self, port=12346, parent=None):
        QThread.__init__(self, parent=parent)
        self.service = None
        self.port = port
        self.parent = parent

    def run(self):
        self.service = serversig.ServerSide(self.port, self.parent)
        self.service.start()
        self.service.join()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
