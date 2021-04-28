from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import clientui as ui
import webbrowser
import receiver
import clientsig


class Main(QMainWindow, ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.start_button.clicked.connect(self.start_button_clicked)
        self.stop_button.clicked.connect(self.stop_button_clicked)
        self.write_welcome_message()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.about_button.clicked.connect(lambda: webbrowser.open('https://github.com/wei-coding/Game-Streaming-Nchu'))

        self.service = None
        self.signal_service = None

    def start_button_clicked(self):
        server_ip = self.serverip_textedit.toPlainText()
        port = self.port_textedit.toPlainText()
        if server_ip == '':
            # self.logs.appendPlainText('Wrong server ip! Please retry.')
            # return
            server_ip = '192.168.31.174'
        if port == '':
            port = 12345
        else:
            port = int(port)
        self.service = ClientService(server_ip, port, self)
        self.logs.appendHtml(f"connect to server: <p style=\"color: red;\">{server_ip}:{port}</p>")
        self.service.start()
        self.signal_service = KeyboardMouse(server_ip, port+1, self)
        self.signal_service.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_button_clicked(self):
        self.service.kill()
        self.signal_service.kill()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def write_welcome_message(self):
        self.logs.appendPlainText('Welcome to GameStreaming Server!')


class ClientService(QThread):
    def __init__(self, server_ip, port, parent=None):
        QThread.__init__(self, parent=parent)
        self.server_ip = server_ip
        self.port = port
        self.parent = parent
        self.service = receiver.Receiver(server_ip, port, parent)
        self.geo = None

    def run(self):
        self.service.start()

    def kill(self):
        self.service.kill()


class KeyboardMouse(QThread):
    def __init__(self, server_ip, port, parent=None):
        QThread.__init__(self, parent)
        self.server_ip = server_ip
        self.port = port
        self.service = None
        self.parent = parent

    def run(self):
        self.service = clientsig.ClientSide(self.server_ip, self.port, self)
        self.service.start()

    def kill(self):
        self.service.kill()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
