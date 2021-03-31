from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import serverui as ui
from waitress import serve
import app
import webbrowser


class Main(QMainWindow, ui.Ui_mainWindow):
    start_sig = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ip = []
        self.iptool = IpService(self.ip, parent=self)
        self.iptool.start()
        self.iptool.finished.connect(self.after_get_ip)
        self.server = Server(parent=self)
        self.about_button.clicked.connect(lambda: webbrowser.open('https://github.com/wei-coding/Game-Streaming-Nchu'))
        self.start_sig.connect(self.after_start)
        self.write_welcome_message()

    def start_clicked(self):
        self.log.append('Server start!')
        self.server.start()

    def after_get_ip(self):
        self.log.append(f'server ip is: {self.ip[0]}')

    def write_welcome_message(self):
        self.log.append('Welcome to GameStreaming Server!')

    def after_start(self):
        self.log.append(f"Server has started at {self.ip[0]}")


class Server(QThread):
    def __init__(self, port=8080, parent=None):
        QThread.__init__(self, parent=parent)
        self.parent = parent

    def run(self):
        serve(app.app, host='0.0.0.0', port=8080)
        self.parent.start_sig.emit()


class IpService(QThread):
    def __init__(self, ret: list, parent=None):
        QThread.__init__(self, parent=parent)
        self.ret = ret

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
