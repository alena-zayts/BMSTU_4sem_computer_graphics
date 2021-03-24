import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets  # инструменты интерфейса
import design  # мой интерфейс
import pyqtgraph as pg  # для цветов на рисунке
from math import pi, sin, cos, radians, floor, ceil  # для математических вычислений
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


def choose_circle_function(alg_name):
    if alg_name == 'Каноническое уравнение':
        return lambda x: circle_canonical(x[0], x[1], x[2], x[3])
    elif alg_name == 'Параметрическое уравнение':
        return lambda x: circle_parametric(x[0], x[1], x[2], x[3])
    elif alg_name == 'Алгоритм Брезенхема':
        return lambda x: circle_brezenham(x[0], x[1], x[2], x[3])
    elif alg_name == 'Алгоритм средней точки':
        return lambda x: circle_midpoint(x[0], x[1], x[2], x[3])
    elif alg_name == 'Библиотечная функция':
        return lambda x: circle_lib(x[0], x[1], x[2], x[3])


def choose_ellipse_function(alg_name):
    if alg_name == 'Каноническое уравнение':
        return lambda x: ellipse_canonical(x[0], x[1], x[2], x[3], x[4])
    elif alg_name == 'Параметрическое уравнение':
        return lambda x: ellipse_parametric(x[0], x[1], x[2], x[3], x[4])
    elif alg_name == 'Алгоритм Брезенхема':
        return lambda x: ellipse_brezenham(x[0], x[1], x[2], x[3], x[4])
    elif alg_name == 'Алгоритм средней точки':
        return lambda x: ellipse_midpoint(x[0], x[1], x[2], x[3], x[4])
    elif alg_name == 'Библиотечная функция':
        return lambda x: ellipse_lib(x[0], x[1], x[2], x[3], x[4])


class MyWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # для доступа к переменным, методам и т.д. в файле design.py
        super().__init__()
        # инициализация дизайна
        self.setupUi(self)

        self.but_circle.clicked.connect(self.on_bt_circle_clicked)
        self.but_circles.clicked.connect(self.on_bt_circles_clicked)
        self.but_ellipse.clicked.connect(self.on_bt_ellipse_clicked)
        self.but_ellipses.clicked.connect(self.on_bt_ellipses_clicked)
        self.but_time.clicked.connect(self.on_bt_time_clicked)
        self.but_axes.clicked.connect(self.on_bt_axes_clicked)
        self.but_clean.clicked.connect(self.on_bt_clean_clicked)

        # рисовать оси - нет
        self.axes_flag = False
        # фигур нет
        self.figures = []

    # обработка ошибки
    def handle_error(self, title, error):
        em = QtWidgets.QMessageBox(self.centralwidget)
        em.setText(error)
        em.setWindowTitle(title)
        em.exec()

    def on_bt_circle_clicked(self):
        # получение данных
        alg_name = self.box_alg.currentText()
        color_name = self.box_color.currentText()
        xc = self.box_c_xc.value()
        yc = self.box_c_yc.value()
        r = self.box_c_r1.value()

        # обработка данных
        color_code = find_color_code(color_name)
        alg_func = choose_circle_function(alg_name)

        # проверка на вырожденность
        if r < 1:
            self.handle_error('Предупреждение',
                              'Окружность, изображенная в пикселях, состоит из 1 точки.')
            dots = [[round(xc), round(yc), color_code]]
        else:
            # построение окружности по выбранному алгоритму
            dots = alg_func([xc, yc, r, color_code])

        # добавление и отрисовка построенных точек
        self.figures.append(dots)
        self.draw_all()

    def on_bt_ellipse_clicked(self):
        # получение данных
        alg_name = self.box_alg.currentText()
        color_name = self.box_color.currentText()
        xc = self.box_e_xc.value()
        yc = self.box_e_yc.value()
        a = self.box_e_a.value()
        b = self.box_e_b.value()

        # обработка данных
        color_code = find_color_code(color_name)
        alg_func = choose_ellipse_function(alg_name)

        # проверка на вырожденность
        if (a < 1) and (b < 1):
            self.handle_error('Предупреждение',
                              'Эллипс, изображенный в пикселях, состоит из 1 точки.')
            dots = [[round(xc), round(yc), color_code]]
        else:
            # построение эллипса по выбранному алгоритму
            dots = alg_func([xc, yc, a, b, color_code])

        # добавление и отрисовка построенных точек
        self.figures.append(dots)
        self.draw_all()

    def on_bt_circles_clicked(self):
        # получение данных
        alg_name = self.box_alg.currentText()
        color_name = self.box_color.currentText()
        xc = self.box_c_xc.value()
        yc = self.box_c_yc.value()
        params = self.box_c_param.currentIndex()
        if params == 0:
            rbeg = self.box_c_r1.value()
            rend = self.box_c_r2.value()
            if rbeg >= rend:
                self.handle_error('Ошибка', 'Начальный радиус должен быть меньше конечного')
                return
            step = self.box_c_step.value()
            n = floor((rend - rbeg) / step) + 1
        elif params == 1:
            rbeg = self.box_c_r1.value()
            rend = self.box_c_r2.value()
            if rbeg >= rend:
                self.handle_error('Ошибка', 'Начальный радиус должен быть меньше конечного')
                return
            n = int(self.box_c_n.value())
        elif params == 2:
            rbeg = self.box_c_r1.value()
            n = int(self.box_c_n.value())
            step = self.box_c_step.value()
            rend = rbeg + step * (n - 1)
        elif params == 3:
            rend = self.box_c_r2.value()
            n = int(self.box_c_n.value())
            step = self.box_c_step.value()
            rbeg = rend - step * (n - 1)

        # обработка данных
        color_code = find_color_code(color_name)
        alg_func = choose_circle_function(alg_name)

        # проверка на вырожденность
        if rbeg < 1:
            self.handle_error('Предупреждение',
                              'Начальная окружность в пикселях представляется одной точкой.')
            dots = [[round(xc), round(yc), color_code]]
            self.figures.append(dots)

        for r in np.linspace(rbeg, rend, n):
            dots = alg_func([xc, yc, r, color_code])
            self.figures.append(dots)

        # отрисовка
        self.draw_all()

    def on_bt_ellipses_clicked(self):
        # получение данных
        alg_name = self.box_alg.currentText()
        color_name = self.box_color.currentText()
        xc = self.box_e_xc.value()
        yc = self.box_e_yc.value()
        a_beg = self.box_e_a.value()
        b_beg = self.box_e_b.value()
        params = self.box_e_param.currentIndex()
        if params == 0:
            a_step = self.box_e_step.value()
            a_n = int(self.box_e_n.value())
            a_end = a_beg + a_step * (a_n - 1)
            a_list = np.linspace(a_beg, a_end, a_n)
            b_list = np.linspace(b_beg, b_beg, a_n)

        elif params == 1:
            b_step = self.box_e_step.value()
            b_n = int(self.box_e_n.value())
            b_end = b_beg + b_step * (b_n - 1)
            a_list = np.linspace(a_beg, a_beg, b_n)
            b_list = np.linspace(b_beg, b_end, b_n)

        # обработка данных
        color_code = find_color_code(color_name)
        alg_func = choose_ellipse_function(alg_name)

        # проверка на вырожденность
        if (a_beg < 1) and (b_beg < 1):
            self.handle_error('Предупреждение',
                              'Начальный эллипс в пикселях представляется одной точкой.')
            dots = [[round(xc), round(yc), color_code]]
            self.figures.append(dots)
        for a, b in list(zip(a_list, b_list)):
            dots = alg_func([xc, yc, a, b, color_code])
            self.figures.append(dots)

        # отрисовка
        self.draw_all()

    def on_bt_axes_clicked(self):
        self.axes_flag = not self.axes_flag
        self.draw_all()
        return

    def on_bt_clean_clicked(self):
        self.axes_flag = False
        self.figures = []
        self.draw_all()

    def draw_all(self):
        # создание сцены
        scene = QtWidgets.QGraphicsScene()
        self.graph.setScene(scene)
        w = self.graph.width()
        h = self.graph.height()
        border = 5
        scene.setSceneRect(-w / 2, -h / 2, w - border, h - border)

        # отрисовка окружностей и эллипсов, построенных по алгоритмам
        width = self.box_width.value()
        for line in self.figures:
            # отрисовка отрезков, построенных библиотекой
            if str(line[0]) == 'lib':
                scene.addEllipse(line[1], line[2], line[3], line[4],
                              pen=pg.mkPen(color=line[5], width=width))
            # если кривая построена алгоритмом
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
        for x0 in range(-w // 2 + 50, w // 2, step):
            scene.addLine(x0, -ser_len / 2, x0, ser_len / 2,
                          pen=pg.mkPen(color=color, width=width))
            text = QtWidgets.QGraphicsTextItem('%d' % x0)
            text.setPos(x0 - step / 5, 0)
            text.update()
            scene.addItem(text)
        # засечки на oy
        for y0 in range(-h // 2 + 50, h // 2, step):
            scene.addLine(-ser_len / 2, y0, ser_len / 2, y0,
                          pen=pg.mkPen(color=color, width=width))
            if y0 != 0:
                text = QtWidgets.QGraphicsTextItem('%d' % y0)
                text.setPos(0, y0 - step / 5)
                text.update()
                scene.addItem(text)

    def count_time_circle_lib(self, n_repeats, r):
        scene = QtWidgets.QGraphicsScene()
        self.graph.setScene(scene)
        w = self.graph.width()
        h = self.graph.height()
        border = 5
        scene.setSceneRect(-w / 2, -h / 2, w - border, h - border)

        x, y = -r, -r
        cw = 2 * r
        ch = 2 * r
        color_code = tuple([0, 0, 0])
        width = 1

        total_sum = 0
        for _ in range(n_repeats):
            start = time()
            scene.addEllipse(x, y, cw, ch,
                             pen=pg.mkPen(color=color_code, width=width))
            end = time()
            total_sum += (end - start)

        self.figures = []
        self.draw_all()
        return total_sum

    def count_time_circle_alg(self, alg_func, n_repeats, r):
        color_code = tuple([0, 0, 0])

        total_sum = 0
        for _ in range(n_repeats):
            start = time()
            alg_func([0, 0, r, color_code])
            end = time()
            total_sum += (end - start)

        return total_sum

    def count_times_circles(self, n_repeats, r_start, r_stop, r_step):
        alg_names = ['Каноническое уравнение', 'Параметрическое уравнение', 'Алгоритм Брезенхема',
                     'Алгоритм средней точки']
        times = []
        for alg_name in alg_names:
            times_cur = []
            alg_func = choose_circle_function(alg_name)
            for r in range(r_start, r_stop, r_step):
                times_cur.append(self.count_time_circle_alg(alg_func, n_repeats, r))
            times.append(times_cur)

        alg_names.append('Библиотечная функция')
        times_cur = []
        for r in range(r_start, r_stop, r_step):
            times_cur.append(self.count_time_circle_lib(n_repeats, r))
        times.append(times_cur)

        return alg_names, times

    def count_time_ellipse_lib(self, n_repeats, a, b):
        scene = QtWidgets.QGraphicsScene()
        self.graph.setScene(scene)
        w = self.graph.width()
        h = self.graph.height()
        border = 5
        scene.setSceneRect(-w / 2, -h / 2, w - border, h - border)

        x, y = -a, -b
        ew = 2 * a
        eh = 2 * b
        color_code = tuple([0, 0, 0])
        width = 1

        total_sum = 0
        for _ in range(n_repeats):
            start = time()
            scene.addEllipse(x, y, ew, eh,
                             pen=pg.mkPen(color=color_code, width=width))
            end = time()
            total_sum += (end - start)

        self.figures = []
        self.draw_all()
        return total_sum

    def count_time_ellipse_alg(self, alg_func, n_repeats, a, b):
        color_code = tuple([0, 0, 0])

        total_sum = 0
        for _ in range(n_repeats):
            start = time()
            alg_func([0, 0, a, b, color_code])
            end = time()
            total_sum += (end - start)

        return total_sum

    def count_times_ellipses(self, n_repeats, a_start, a_stop, a_step):
        alg_names = ['Каноническое уравнение', 'Параметрическое уравнение', 'Алгоритм Брезенхема',
                     'Алгоритм средней точки']
        times = []
        for alg_name in alg_names:
            times_cur = []
            alg_func = choose_ellipse_function(alg_name)
            for a in range(a_start, a_stop, a_step):
                times_cur.append(self.count_time_ellipse_alg(alg_func, n_repeats, a, a))
            times.append(times_cur)

        alg_names.append('Библиотечная функция')
        times_cur = []
        for r in range(a_start, a_stop, a_step):
            times_cur.append(self.count_time_ellipse_lib(n_repeats, a, a))
        times.append(times_cur)

        return times


    def on_bt_time_clicked(self):
        n_repeats = 20
        r_start, r_stop, r_step = 100, 2001, 200
        rs = np.linspace(100, 2000, 10, dtype=int)
        alg_names, times_circle = self.count_times_circles(n_repeats, r_start, r_stop, r_step)
        times_ellipse = self.count_times_ellipses(n_repeats, r_start, r_stop, r_step)

        plt.rcParams['font.size'] = '16'
        fig, (ax1, ax2) = plt.subplots(
            nrows=2, ncols=1,
            figsize=(25, 20)
        )
        ax1.set_title('Время, затраченное на построение %d окружностей с центром в '
                      'точке (0, 0) в зависимости от радиуса'
                      % n_repeats)
        ax1.set_xlabel('Радиус')
        ax1.set_ylabel('Время, c')
        ax1.grid()

        for i in range(len(alg_names)):
            alg_name = alg_names[i]
            time = times_circle[i]
            ax1.plot(rs, time, label=alg_name)
        ax1.legend(loc='best')

        ax2.set_title('Время, затраченное на построение %d эллипсов с центром в '
                      'точке (0, 0) в зависимости от полуосей (a=b)'
                      % n_repeats)
        ax2.set_xlabel('Полуось')
        ax2.set_ylabel('Время, c')
        ax2.grid()

        for i in range(len(alg_names)):
            alg_name = alg_names[i]
            time = times_ellipse[i]
            ax2.plot(rs, time, label=alg_name)
        ax2.legend(loc='best')
        plt.show()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MyWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':
    main()
