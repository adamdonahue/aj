import sys

from PySide.QtCore import *
from PySide.QtGui import *

class Form(QDialog):
    def onClick(self, *args, **kwargs):
        print args
        print kwargs

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.setWindowTitle("QDialog")
        button = QPushButton("Click me!")
        button.clicked.connect(self.onClick)
        layout = QVBoxLayout()
        layout.addWidget(button)
        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
