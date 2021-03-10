import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets  # инструменты интерфейса
import design  # мой интерфейс
import pyqtgraph as pg  # для цветов на рисунке
from math import pi, sin, cos, radians, floor  # для математических вычислений
from time import time  # для подсчета времени
import matplotlib.pyplot as plt  # для графиков
import numpy as np
from algorythms import *  # реалмзованные алгоритмы

EPS = 1e-6


def find_color_code(color_name):
    if color_name == 'Цвет фона':
        return tuple([255, 255, 255])
    elif color_name == 'Красный':
        return tuple([255, 0, 0])
    elif color_name == 'Зеленый':
        return tuple([0, 255, 0])
    elif color_name == 'Синий':
        return tuple([0, 0, 255])
    elif color_name == 'Желтый':
        return tuple([255, 255, 0])
    elif color_name == 'Розовый':
        return tuple([255, 0, 255])
    elif color_name == 'Черный':
        return tuple([0, 0, 0])


def choose_function(alg_name):
    if alg_name == 'ЦДА':
        return lambda x: dda(x[0], x[1], x[2], x[3], x[4])
    elif alg_name == 'Брезенхем (действ.)':
        return lambda x: brezenham_float(x[0], x[1], x[2], x[3], x[4])
    elif alg_name == 'Брезенхем (цел.)':
        return lambda x: brezenham_int(x[0], x[1], x[2], x[3], x[4])
    elif alg_name == 'Брезенхем (устр. ступенч.)':
        return lambda x: brezenham_del_stag(x[0], x[1], x[2], x[3], x[4])
    elif alg_name == 'Ву':
        return lambda x: wu(x[0], x[1], x[2], x[3], x[4])
    elif alg_name == 'Библиотечная функция':
        return lambda x: lib(x[0], x[1], x[2], x[3], x[4])


class MyWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # для доступа к переменным, методам и т.д. в файле design.py
        super().__init__()
        # инициализация дизайна
        self.setupUi(self)

        self.but_single.clicked.connect(self.on_bt_single_clicked)
        self.but_bunch.clicked.connect(self.on_bt_bunch_clicked)
        self.but_time.clicked.connect(self.on_bt_time_clicked)
        self.but_step.clicked.connect(self.on_bt_step_clicked)
        self.but_axes.clicked.connect(self.on_bt_axes_clicked)
        self.but_clean.clicked.connect(self.on_bt_clean_clicked)

        # рисовать оси - нет
        self.axes_flag = False
        # отрезков нет
        self.lines = []

    # обработка ошибки
    def handle_error(self, title, error):
        em = QtWidgets.QMessageBox(self.centralwidget)
        em.setText(error)
        em.setWindowTitle(title)
        em.exec()

    def on_bt_single_clicked(self):
        # получение данных
        alg_name = self.box_alg.currentText()
        color_name = self.box_color.currentText()
        xn = self.box_xn.value()
        xk = self.box_xk.value()
        yn = self.box_yn.value()
        yk = self.box_yk.value()

        # обработка данных
        color_code = find_color_code(color_name)
        alg_func = choose_function(alg_name)

        # проверка отрезка на вырожденность
        if (abs(round(xn) - round(xk)) < 1) and (abs(round(yn) - round(yk)) < 1):
            self.handle_error('Предупреждение',
                              'Отрезок, изображенный в пикселях, состоит из 1 точки.')
            dots = [[round(xn), round(yn), color_code]]
        else:
            # построение отрезка по выбранному алгоритму
            dots = alg_func([xn, yn, xk, yk, color_code])

        # добавление и отрисовка построенных точек
        self.lines.append(dots)
        self.draw_lines()

    def on_bt_bunch_clicked(self):
        # получение данных
        alg_name = self.box_alg.currentText()
        color_name = self.box_color.currentText()
        xn = self.box_xc.value()
        yn = self.box_yc.value()
        length = self.box_len.value()
        step = self.box_step.value() * pi / 180

        # обработка данных
        color_code = find_color_code(color_name)
        alg_func = choose_function(alg_name)

        # проверка отрезка на вырожденность
        if length < 1:
            self.handle_error('Предупреждение',
                              'Отрезки, изображенные в пикселях, сводятсся к 1 точке.')
            dots = [[round(xn), round(yn), color_code]]
            self.lines.append(dots)
        else:
            angle = 0
            while 2 * pi - angle > EPS:
                xk = xn + length * cos(angle)
                yk = yn + length * sin(angle)
                # построение отрезка по выбранному алгоритму
                dots = alg_func([xn, yn, xk, yk, color_code])
                # добавление построенных точек
                self.lines.append(dots)

                angle += step
        # отрисовка
        self.draw_lines()

    def on_bt_time_clicked(self):
        n_repeats = 50
        alg_names, times = self.count_times(n_repeats)
        plt.figure(figsize=(25, 10))
        plt.rcParams['font.size'] = '16'
        plt.xlabel('Алгоритм')
        plt.ylabel('Время, c')
        plt.title('Время, затраченное на построение %d спектров с центром в\n '
                  'точке (0, 0), отрезками длиной 300 с шагом в 10 градусов.'
                  % n_repeats)
        plt.bar(alg_names, times)
        plt.show()

    def on_bt_step_clicked(self):
        length = 1000
        alg_names, steps_total = self.count_steps_in_algs(length)

        plt.figure(figsize=(25, 10))
        plt.rcParams['font.size'] = '16'
        plt.xlabel('Угол наклона, °')
        plt.xticks(np.arange(0, 361, 15, dtype='int64'))
        plt.ylabel('Количество ступенек')
        plt.title('График зависимости количества ступенек от\n'
                  'угла наклона отрезка длины %d' % length)
        angles = np.arange(0, 360, 1, dtype='int64')
        for i in range(6):
            plt.plot(angles, steps_total[i], label=alg_names[i])
        plt.legend()
        plt.xlim([0, 90])
        plt.show()

    def on_bt_axes_clicked(self):
        self.axes_flag = not self.axes_flag
        self.draw_lines()
        return

    def on_bt_clean_clicked(self):
        self.axes_flag = False
        self.lines = []
        self.draw_lines()

    def draw_lines(self):
        # создание сцены
        scene = QtWidgets.QGraphicsScene()
        self.graph.setScene(scene)
        w = self.graph.width()
        h = self.graph.height()
        border = 5
        scene.setSceneRect(-w / 2, -h / 2, w - border, h - border)
        # scene.setSceneRect(0, 0, w, h) если 0, 0 в углу

        # отрисовка отрезков, построенных по алгоритмам
        width = self.box_width.value()
        for line in self.lines:
            # отрисовка отрезков, построенных библиотекой
            if str(line[0]) == 'lib':
                scene.addLine(line[1], line[2], line[3], line[4],
                              pen=pg.mkPen(color=line[5], width=width))
            # если прямая построена алгоритмом
            else:
                # высвечивание пикселов
                for dot in line:
                    scene.addLine(dot[0], dot[1], dot[0], dot[1],
                                  pen=pg.mkPen(color=dot[2], width=width))

        # отрисовка осей в случае необходимости
        if self.axes_flag:
            self.draw_axes(scene, w, h)

        # вывод
        self.graph.repaint()
        self.repaint()

    def draw_axes(self, scene, w, h):
        # оси
        color = '#808080'
        width = self.box_width.value()
        # ox
        scene.addLine(-w / 2, 0, w / 2, 0,
                      pen=pg.mkPen(color=color, width=width))
        # стрелочки
        scene.addLine(-w / 70, h / 2.2, 0, h / 2,
                      pen=pg.mkPen(color=color, width=width))
        scene.addLine(w / 70, h / 2.2, 0, h / 2,
                      pen=pg.mkPen(color=color, width=width))
        # oy
        scene.addLine(0, -h, 0, h,
                      pen=pg.mkPen(color=color, width=width))
        # стрелочки
        scene.addLine(w / 2.1, -h / 60, w / 2, 0,
                      pen=pg.mkPen(color=color, width=width))
        scene.addLine(w / 2.1, h / 60, w / 2, 0,
                      pen=pg.mkPen(color=color, width=width))
        # засечки на ox
        ser_len = 10
        step = 100
        width = 1
        for x0 in range(-w // 2 + 100, w // 2, step):
            scene.addLine(x0, -ser_len / 2, x0, ser_len / 2,
                          pen=pg.mkPen(color=color, width=width))
            text = QtWidgets.QGraphicsTextItem('%d' % x0)
            text.setPos(x0 - step / 5, 0)
            text.update()
            scene.addItem(text)
        # засечки на oy
        for y0 in range(-h // 2 + 100, h // 2, step):
            scene.addLine(-ser_len / 2, y0, ser_len / 2, y0,
                          pen=pg.mkPen(color=color, width=width))
            if y0 != 0:
                text = QtWidgets.QGraphicsTextItem('%d' % y0)
                text.setPos(0, y0 - step / 5)
                text.update()
                scene.addItem(text)

    def count_time_lib(self, n_repeats):
        scene = QtWidgets.QGraphicsScene()
        self.graph.setScene(scene)
        w = self.graph.width()
        h = self.graph.height()
        border = 5
        scene.setSceneRect(-w / 2, -h / 2, w - border, h - border)

        xn = 0
        yn = 0
        length = 300
        step = 10 * pi / 180
        color_code = tuple([0, 0, 0])
        width = 1

        total_sum = 0
        for i in range(n_repeats):
            angle = 0
            while 2 * pi - angle > EPS:
                xk = xn + length * cos(angle)
                yk = yn + length * sin(angle)
                # построение отрезка по выбранному алгоритму
                start = time()
                scene.addLine(xn, yn, xk, yk,
                              pen=pg.mkPen(color=color_code, width=width))
                end = time()
                total_sum += (end - start)
                angle += step

        self.lines = []
        self.draw_lines()
        return total_sum

    def count_time_alg(self, alg_func, n_repeats):
        xn = 0
        yn = 0
        length = 300
        step = 10 * pi / 180
        color_code = tuple([0, 0, 0])

        total_sum = 0
        for i in range(n_repeats):
            angle = 0
            while 2 * pi - angle > EPS:
                xk = xn + length * cos(angle)
                yk = yn + length * sin(angle)
                # построение отрезка по выбранному алгоритму
                start = time()
                alg_func([xn, yn, xk, yk, color_code])
                end = time()
                total_sum += (end - start)
                angle += step
        return total_sum

    def count_times(self, n_repeats):
        alg_names = ['ЦДА', 'Брезенхем (действ.)', 'Брезенхем (цел.)',
                     'Брезенхем (устр. ступенч.)', 'Ву']
        times = []
        for alg_name in alg_names:
            alg_func = choose_function(alg_name)
            times.append(self.count_time_alg(alg_func, n_repeats))

        alg_names.append('Библиотечная функция')
        times.append(self.count_time_lib(n_repeats))

        return alg_names, times

    def count_steps_in_line(self, line):
        min_x = min(line[0][0], line[-1][0])
        max_x = max(line[0][0], line[-1][0])
        min_y = min(line[0][1], line[-1][1])
        max_y = max(line[0][1], line[-1][1])
        dx = max_x - min_x
        dy = max_y - min_y

        return min(dx, dy)

    def count_steps_in_spector(self, alg_func, length):
        xn = 0
        yn = 0
        step = radians(1)
        color_code = (0, 0, 0)
        angle = 0
        steps_amount = []
        while 2 * pi - angle > EPS:
            xk = xn + length * cos(angle)
            yk = yn + length * sin(angle)
            # построение отрезка по выбранному алгоритму
            line = alg_func([xn, yn, xk, yk, color_code])
            steps_amount.append(self.count_steps_in_line(line))
            angle += step
        return steps_amount

    def count_steps_in_algs(self, length):
        alg_names = ['ЦДА', 'Брезенхем (действ.)', 'Брезенхем (цел.)',
                     'Брезенхем (устр. ступенч.)', 'Ву']
        stpes_total = []
        for alg_name in alg_names:
            alg_func = choose_function(alg_name)
            stpes_total.append(self.count_steps_in_spector(alg_func, length))

        alg_names.append('Теоретическое ожидание')
        steps_theor = []
        for angle in range(360):
            sin_angle = sin(radians(angle))
            cos_angle = cos(radians(angle))
            dx = abs(length * cos_angle)
            dy = abs(length * sin_angle)
            steps_theor.append(floor(min(dx, dy)))
        stpes_total.append(steps_theor)

        return alg_names, stpes_total

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MyWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':
    main()
