import sys
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QApplication, QPushButton
from PyQt5.Qt import QInputDialog, QPushButton, QGridLayout, QMessageBox


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.L = QLineEdit()
        self.v1 = QLineEdit()
        self.v2 = QLineEdit()
        self.t1 = QLineEdit()
        self.t2 = QLineEdit()
        self.T1 = QLineEdit()
        self.T2 = QLineEdit()

        redb = QPushButton('Red', self)

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel('Высота подъема и опускания стола'), 0, 0)
        layout.addWidget(self.L, 0, 1)

        layout.addWidget(QLabel('Скорость подъема стола'), 1, 0)
        layout.addWidget(self.v1, 1, 1)

        layout.addWidget(QLabel('Скорость опускания (ретракта) стола'), 2, 0)
        layout.addWidget(self.v2, 2, 1)

        layout.addWidget(QLabel('Скорость подъема стола'), 3, 0)
        layout.addWidget(QLabel('none'), 3, 1)
        #layout.addWidget(self.t1, 3, 1)

        layout.addWidget(QLabel('Скорость опускания (ретракта) стола'), 4, 0)
        layout.addWidget(QLabel('none'), 4, 1)
        #layout.addWidget(self.t2, 4, 1)

        layout.addWidget(QLabel('Минимальная задержка выключения'), 5, 0)
        layout.addWidget(QLabel('none'), 5, 1)
        #layout.addWidget(self.T1, 5, 1)

        layout.addWidget(QLabel('Максимальная задержка выключения'), 6, 0)
        layout.addWidget(QLabel('none'), 6, 1)
        #layout.addWidget(self.T2, 6, 1)

        layout.addWidget(redb, 7, 0)



if __name__ == '__main__':
    app = QApplication([])

    window = Window()
    window.show()

    app.exec()