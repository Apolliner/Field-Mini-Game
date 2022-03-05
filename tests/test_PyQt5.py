import sys
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QApplication, QPushButton
from PyQt5.Qt import QInputDialog, QPushButton, QGridLayout, QMessageBox


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.L = QLineEdit()
        self.v1 = QLineEdit()
        self.v2 = QLineEdit()
        self.t1 = QLabel('-')
        self.t2 = QLabel('-')
        self.T1 = QLabel('-')
        self.T2 = QLabel('-')
        self.error = QLabel('')

        calc_button = QPushButton('Рассчёт', self)

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel('Высота подъема и опускания стола'), 0, 0)
        layout.addWidget(self.L, 0, 1)

        layout.addWidget(QLabel('Скорость подъема стола'), 1, 0)
        layout.addWidget(self.v1, 1, 1)

        layout.addWidget(QLabel('Скорость опускания (ретракта) стола'), 2, 0)
        layout.addWidget(self.v2, 2, 1)

        layout.addWidget(QLabel('Скорость подъема стола'), 3, 0)
        layout.addWidget(self.t1, 3, 1)
        #layout.addWidget(self.t1, 3, 1)

        layout.addWidget(QLabel('Скорость опускания (ретракта) стола'), 4, 0)
        layout.addWidget(self.t2, 4, 1)
        #layout.addWidget(self.t2, 4, 1)

        layout.addWidget(QLabel('Минимальная задержка выключения'), 5, 0)
        layout.addWidget(self.T1, 5, 1)
        #layout.addWidget(self.T1, 5, 1)

        layout.addWidget(QLabel('Максимальная задержка выключения'), 6, 0)
        layout.addWidget(self.T2, 6, 1)
        #layout.addWidget(self.T2, 6, 1)

        layout.addWidget(calc_button, 7, 0)
        layout.addWidget(self.error, 7, 1)
        calc_button.clicked.connect(self.calc_action)

    def calc_action(self):
        try:
            L = float(self.L.text())
            v1 = float(self.v1.text())
            v2 = float(self.v2.text())
            t1 = L/(v1/60)
            t2 = L/(v2/60)
            T1 = t1 + t2 + 2
            T2 = t1 + t2 + 3
            self.t1.setText(str(round(t1, 2)))
            self.t2.setText(str(round(t2, 2)))
            self.T1.setText(str(round(T1, 2)))
            self.T2.setText(str(round(T2, 2)))
            self.error.setText("")
        except:
            self.t1.setText('-')
            self.t2.setText('-')
            self.T1.setText('-')
            self.T2.setText('-')
            self.error.setText("Wrong Input")

if __name__ == '__main__':
    app = QApplication([])

    window = Window()
    window.show()

    app.exec()