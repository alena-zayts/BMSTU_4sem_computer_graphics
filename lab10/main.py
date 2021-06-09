import design  # мой интерфейс
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QPen, QImage, QPixmap, QPainter, QBrush, QPolygon, QColor
from PyQt5.QtCore import Qt, QPoint
import sys
from copy import deepcopy
import numpy as np
from functions import *
from floating_horizont import *
import pyqtgraph as pg  # для цветов на рисунке
global w


# код цвета по названию
def find_color_code(color_name):
    if color_name == 'Красный':
        return 0xC52B1B
    elif color_name == 'Зеленый':
        return 0x62F20D
    elif color_name == 'Синий':
        return 0x0B108E
    elif color_name == 'Желтый':
        return 0xD4E006
    elif color_name == 'Голубой':
        return 0x3B93E8
    elif color_name == 'Бирюзовый':
        return 0x3BE8E8
    elif color_name == 'Розовый':
        return 0xE23BE8
    elif color_name == 'Белый':
        return 0xFFFFFF


class MyWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # для доступа к переменным, методам и т.д. в файле design.py
        super().__init__()
        # инициализация дизайна
        self.setupUi(self)

        self.scene = QtWidgets.QGraphicsScene(0, 0, 1400, 1400)
        self.scene.win = self
        self.graph.setScene(self.scene)
        self.image = QImage(1400, 1400, QImage.Format_RGB32)
        self.image.fill(Qt.black)
        pix = QPixmap()
        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)

        # настройка кнопок
        self.but_clean.clicked.connect(self.on_bt_clean_clicked)
        self.but_turnx.clicked.connect(self.on_bt_turnx_clicked)
        self.but_turny.clicked.connect(self.on_bt_turny_clicked)
        self.but_turnz.clicked.connect(self.on_bt_turnz_clicked)
        self.but_scale.clicked.connect(self.on_bt_scale_clicked)
        self.but_draw.clicked.connect(self.on_bt_draw_clicked)
        self.but_limits.clicked.connect(self.on_bt_draw_clicked)
        self.but_del_coefs.clicked.connect(self.del_coefs)
        self.width_draw = 1

        self.xangle = 0
        self.yangle = 0
        self.zangle = 0
        self.coef = 1
        self.result = []

    def del_coefs(self):
        self.xangle = 0
        self.yangle = 0
        self.zangle = 0
        self.coef = 1

    # обработка ошибки
    def handle_error(self, title, error):
        em = QtWidgets.QMessageBox(self.centralwidget)
        em.setText(error)
        em.setWindowTitle(title)
        em.exec()

    # очистка экрана
    def on_bt_clean_clicked(self):
        self.image.fill(Qt.black)
        pix = QPixmap()
        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)

    def input_all(self):
        self.xbeg = self.box_xbeg.value()
        self.xend = self.box_xend.value()
        self.xstep = self.box_xstep.value()
        self.zbeg = self.box_zbeg.value()
        self.zend = self.box_zend.value()
        self.zstep = self.box_zstep.value()
        color_name = self.box_color.currentText()
        self.color_draw = find_color_code(color_name)
        self.function = funcs_list[self.box_function.currentIndex()]

    def on_bt_turnx_clicked(self):
        self.xangle += self.box_xangle.value()
        self.on_bt_draw_clicked()

    def on_bt_turny_clicked(self):
        self.yangle += self.box_yangle.value()
        self.on_bt_draw_clicked()

    def on_bt_turnz_clicked(self):
        self.zangle += self.box_zangle.value()
        self.on_bt_draw_clicked()

    def on_bt_scale_clicked(self):
        self.coef *= self.box_coef.value()
        self.on_bt_draw_clicked()

    def on_bt_draw_clicked(self):
        self.input_all()
        if self.xbeg >= self.xend:
            self.handle_error('Ошибка', ' Начальное значение x должно быть меньше конечного')
            return
        if self.zbeg >= self.zend:
            self.handle_error('Ошибка', ' Начальное значение z должно быть меньше конечного')
            return

        self.image.fill(Qt.black)
        self.image = float_horizon(self.scene.width(), self.scene.height(),
                                   self.xbeg, self.xend, self.xstep,
                                   self.zbeg, self.zend, self.zstep,
                                   self.xangle, self.yangle, self.zangle, self.coef,
                                   self.function, self.image, self.color_draw)

        pix = QPixmap()
        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    w = MyWindow()  # Создаём объект класса ExampleApp
    w.show()  # Показываем окно
    sys.exit(app.exec_())  # и запускаем приложение
