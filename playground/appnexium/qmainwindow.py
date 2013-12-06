import sys

from PySide.QtCore import *
from PySide.QtGui import *

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Test")

        workspace = QWorkspace()
        self.setCentralWidget(workspace)

        crw = ChatRoomWindow()

        mapper = QSignalMapper(self)
        mapper.mapped.connect(workspace.setActiveWindow)

    def enableActions(self):
        pass

    


class ChatRoomWindow(QTextEdit):

    def __init__(self, parent=None):
        super(ChatRoomWindow, self).__init__(parent)
        self.setWindowTitle("test")
        self.document().modificationChanged.connect(self.setWindowModified)

        self._isSafeToClose = False
    
    def closeEvent(self, *args, **kwargs):
        pass

    def isSafeToClose(self):
        return self._isSafeToClose



def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
