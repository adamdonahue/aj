import sys

from PySide.QtCore import *
from PySide.QtGui import *

class AppnexiumMessage(object):
    def __init__(self):
        pass

class AppnexiumRoom(object):
    def __init__(self, type=None):
        self.type = type
        self.messages = []

    def addMessage(self, message):
        self

class Appnexium(object):
    def __init__(self):
        self.user = None
        self.availableRooms= []
        self.openRooms = []
        self.roster = []



class AppnexiumUI(QApplication):
    """An AppNexus-centric chat client."""

    def __init__(self, parent=None):
        super(Appnexium, self).__init__(parent)

    def panel(self):
        mainWindow = QMainWindow()
        mainWindow.setWindowTitle("AppNexium")
        return mainWindow

    def show(self):
        p = self.panel()
        p.show()
        self.exec_()
        return self

def main():
    appnexium = AppnexiumUI(sys.argv)
    appnexium.show()
    return appnexium

if __name__ == '__main__':
    main()
