from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import clientui as ui
import webbrowser
import receiver


class Main(QMainWindow, ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.start_button.clicked.connect(self.start_button_clicked)
        self.stop_button.clicked.connect(self.stop_button_clicked)
        self.about_button.clicked.connect(lambda: webbrowser.open('https://github.com/wei-coding/Game-Streaming-Nchu'))

    def start_button_clicked(self):
        pass

    def stop_button_clicked(self):
        pass


class ClientService(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent=parent)

    def run(self):
        pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
