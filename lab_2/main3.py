import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets  # инструменты интерфейса
import design  # мой интерфейс
import pyqtgraph as pg  # для цветов на рисунке
import numpy as np  # для обработки массивов
from math import pi, sin, cos, radians  # для математических вычислений
from copy import deepcopy  # для копирования списков


class MyWindow(QtWidgets.QMainWindow, design.Ui_root):
    def __init__(self):
        # для доступа к переменным, методам и т.д. в файле design.py
        super().__init__()
        # инициализация дизайна
        self.setupUi(self)
        self.graph.scale(1, -1)

        # настройка кнопок
        self.bt_shift.clicked.connect(self.shift)
        self.bt_scale.clicked.connect(self.scale)
        self.bt_turn.clicked.connect(self.turn)
        self.bt_again.clicked.connect(self.again)
        self.bt_back.clicked.connect(self.back)

        # начальные точки
        # центр изображения
        self.centre_init = [{'x': 0, 'y': 0}]
        # сам дом
        self.house_init = [{'x': -400, 'y': -250}, {'x': -400, 'y': 100},
                           {'x': 0, 'y': 250}, {'x': 400, 'y': 100},
                           {'x': 400, 'y': -250}]
        # окно на чердаке
        self.attic_init = [{'x': -25, 'y': 125}, {'x': -25, 'y': 150},
                           {'x': 0, 'y': 150}, {'x': 0, 'y': 125},
                           {'x': 25, 'y': 125}, {'x': 25, 'y': 150},
                           {'x': 25, 'y': 175}, {'x': 0, 'y': 175},
                           {'x': -25, 'y': 175}]
        # крест - перемычки на окне
        self.window_plus_init = [{'x': -300, 'y': 0}, {'x': -200, 'y': 0},
                                 {'x': -250, 'y': 50}, {'x': -250, 'y': -50}]
        # круг - рамка окна
        self.window_circ_param = {'xc': -250, 'yc': 0, 'r': 50}
        self.window_circ_intit = []
        # из параметрического уравнения окружности
        # x = xc + r * cos(t),
        # y = yc + r * sin(t),
        # t in [0, 2 * pi]
        t = np.linspace(0, 2 * pi, 1000)
        for t_cur in t:
            x0 = self.window_circ_param['xc'] + self.window_circ_param['r'] * cos(t_cur)
            y0 = self.window_circ_param['yc'] + self.window_circ_param['r'] * sin(t_cur)
            self.window_circ_intit.append({'x': x0, 'y': y0})
        # ромб на двери
        self.door_rhomb_init = [{'x': 200, 'y': 0}, {'x': 250, 'y': -100},
                                {'x': 200, 'y': -200}, {'x': 150, 'y': -100}]
        # эллипс на двери
        self.door_el_param = {'xc': 200, 'yc': -100, 'a': 50, 'b': 100}
        self.door_el_init = []
        # из параметрического уравнения эллипса
        # x = xc + a * cos(t),
        # y = yc + b * sin(t),
        # t in [0, 2 * pi]
        t = np.linspace(0, 2 * pi, 1000)
        for t_cur in t:
            x0 = self.door_el_param['xc'] + self.door_el_param['a'] * cos(t_cur)
            y0 = self.door_el_param['yc'] + self.door_el_param['b'] * sin(t_cur)
            self.door_el_init.append({'x': x0, 'y': y0})

        # объединение всех элементов исходного изображения
        self.elements_init = {'centre': self.centre_init, 'house': self.house_init,
                              'attic': self.attic_init, 'window_circ': self.window_circ_intit,
                              'window_plus': self.window_plus_init, 'door_el': self.door_el_init,
                              'door_rhomb': self.door_rhomb_init}
        # текущие и предыдущие точки инициализируются начальными
        self.elements_cur = deepcopy(self.elements_init)
        self.elements_prev = deepcopy(self.elements_init)
        # отрисовка
        self.paint()

    # рисование изображения в текущих координатах
    def paint(self):
        # извлечение необходимых объектов
        centre = self.elements_cur['centre']
        house = self.elements_cur['house']
        attic = self.elements_cur['attic']
        window_circ = self.elements_cur['window_circ']
        window_plus = self.elements_cur['window_plus']
        door_el = self.elements_cur['door_el']
        door_rhomb = self.elements_cur['door_rhomb']

        # указание центра фигуры
        self.en_x0.setText('%d' % round(centre[0]['x'], 0))
        self.en_y0.setText('%d' % round(centre[0]['y'], 0))

        # создание сцены
        scene = QtWidgets.QGraphicsScene()
        self.graph.setScene(scene)
        w = self.graph.width()
        h = self.graph.height()
        border = 5
        scene.setSceneRect(-w / 2, -h / 2, w - border, h - border)

        # оси
        color = '#C0C0C0'
        width = 2
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
        for x0 in range(-w // 2 + 50, w // 2, step):
            scene.addLine(x0, -ser_len / 2, x0, ser_len / 2,
                          pen=pg.mkPen(color=color, width=width))
            text = QtWidgets.QGraphicsTextItem('%d' % x0)
            text.setPos(x0 - step / 5, 0)
            text.scale(1, -1)
            text.update()
            scene.addItem(text)
        # засечки на oy
        for y0 in range(-h // 2 + 50, h // 2, step):
            scene.addLine(-ser_len / 2, y0, ser_len / 2, y0,
                          pen=pg.mkPen(color=color, width=width))
            if y0 != 0:
                text = QtWidgets.QGraphicsTextItem('%d' % y0)
                text.setPos(0, y0 + step / 5)
                text.scale(1, -1)
                text.update()
                scene.addItem(text)
        # сам дом
        color = '#1E90FF'
        width = 4
        for i in range(len(house) - 1):
            scene.addLine(house[i]['x'], house[i]['y'],
                          house[i + 1]['x'], house[i + 1]['y'],
                          pen=pg.mkPen(color=color, width=width))

        scene.addLine(house[1]['x'], house[1]['y'],
                      house[3]['x'], house[3]['y'],
                      pen=pg.mkPen(color=color, width=width))
        scene.addLine(house[0]['x'], house[0]['y'],
                      house[4]['x'], house[4]['y'],
                      pen=pg.mkPen(color=color, width=width))
        # окно на чердаке
        color = '#9ACD32'
        for i in range(len(attic) - 1):
            scene.addLine(attic[i]['x'], attic[i]['y'],
                          attic[i + 1]['x'], attic[i + 1]['y'],
                          pen=pg.mkPen(color=color, width=width))
        scene.addLine(attic[1]['x'], attic[1]['y'],
                      attic[8]['x'], attic[8]['y'],
                      pen=pg.mkPen(color=color, width=width))
        scene.addLine(attic[0]['x'], attic[0]['y'],
                      attic[3]['x'], attic[3]['y'],
                      pen=pg.mkPen(color=color, width=width))
        scene.addLine(attic[2]['x'], attic[2]['y'],
                      attic[5]['x'], attic[5]['y'],
                      pen=pg.mkPen(color=color, width=width))
        scene.addLine(attic[2]['x'], attic[2]['y'],
                      attic[7]['x'], attic[7]['y'],
                      pen=pg.mkPen(color=color, width=width))

        # крест - перемычки на окне
        color = '#DB7093'
        scene.addLine(window_plus[0]['x'], window_plus[0]['y'],
                      window_plus[1]['x'], window_plus[1]['y'],
                      pen=pg.mkPen(color=color, width=width))
        scene.addLine(window_plus[2]['x'], window_plus[2]['y'],
                      window_plus[3]['x'], window_plus[3]['y'],
                      pen=pg.mkPen(color=color, width=width))

        # круг - рамка окна
        for dot in window_circ:
            scene.addLine(dot['x'], dot['y'], dot['x'], dot['y'],
                          pen=pg.mkPen(color=color, width=width))
        # ромб на двери
        color = '#D2691E'
        for i in range(len(door_rhomb) - 1):
            scene.addLine(door_rhomb[i]['x'], door_rhomb[i]['y'],
                          door_rhomb[i + 1]['x'], door_rhomb[i + 1]['y'],
                          pen=pg.mkPen(color=color, width=width))
        scene.addLine(door_rhomb[3]['x'], door_rhomb[3]['y'],
                      door_rhomb[0]['x'], door_rhomb[0]['y'],
                      pen=pg.mkPen(color=color, width=width))
        scene.addLine(door_rhomb[0]['x'], door_rhomb[0]['y'],
                      door_rhomb[2]['x'], door_rhomb[2]['y'],
                      pen=pg.mkPen(color=color, width=width))
        scene.addLine(door_rhomb[1]['x'], door_rhomb[1]['y'],
                      door_rhomb[3]['x'], door_rhomb[3]['y'],
                      pen=pg.mkPen(color=color, width=width))
        # эллипс на двери
        for dot in door_el:
            scene.addLine(dot['x'], dot['y'], dot['x'], dot['y'],
                          pen=pg.mkPen(color=color, width=width))
        self.graph.repaint()
        self.repaint()

    # обработка ошибки
    def handle_error(self, error):
        em = QtWidgets.QMessageBox(self.centralwidget)
        em.setText(error)
        em.setWindowTitle('Ошибка')
        em.exec()

    # перенос
    def shift(self):
        # получение параметров и обработка ошибок
        dx = self.en_dx.text()
        try:
            dx = float(dx)
        except:
            self.handle_error('Введено некорректное значение смещения dx')
            return
        dy = self.en_dy.text()
        try:
            dy = float(dy)
        except:
            self.handle_error('Введено некорректное значение смещения dy')
            return
        # перемещение изображения
        self.elements_prev = deepcopy(self.elements_cur)
        for element in self.elements_cur.values():
            for dot in element:
                dot['x'] += dx
                dot['y'] += dy
        self.paint()

    # масштабирование
    def scale(self):
        # получение параметров и обработка ошибок
        kx = self.en_kx.text()
        try:
            kx = float(kx)
        except:
            self.handle_error('Введено некорректное значение коэффициента масштабирования kx')
            return
        ky = self.en_ky.text()
        try:
            ky = float(ky)
        except:
            self.handle_error('Введено некорректное значение коэффициента масштабирования ky')
            return
        xm = self.en_xm.text()
        try:
            xm = float(xm)
        except:
            self.handle_error('Введено некорректное значение координаты центра масштабирования xm')
            return
        ym = self.en_ym.text()
        try:
            ym = float(ym)
        except:
            self.handle_error('Введено некорректное значение координаты центра масштабирования ym')
            return
        # масштабирование изображения
        self.elements_prev = deepcopy(self.elements_cur)
        for element in self.elements_cur.values():
            for dot in element:
                dot['x'] = kx * dot['x'] + xm * (1 - kx)
                dot['y'] = ky * dot['y'] + ym * (1 - ky)
        self.paint()

    # поворот
    def turn(self):
        # получение параметров и обработка ошибок
        xc = self.en_xc.text()
        try:
            xc = float(xc)
        except:
            self.handle_error('Введено некорректное значение координаты центра поворота xc')
            return
        yc = self.en_yc.text()
        try:
            yc = float(yc)
        except:
            self.handle_error('Введено некорректное значение координаты центра поворота yc')
            return
        teta = self.en_teta.text()
        try:
            teta = float(teta)
            teta = radians(teta)
        except:
            self.handle_error('Введено некорректное значение угла поворота ϴ')
            return

        self.elements_prev = deepcopy(self.elements_cur)
        for element in self.elements_cur.values():
            for dot in element:
                x_new = xc + (dot['x'] - xc) * cos(teta) + (dot['y'] - yc) * sin(teta)
                y_new = yc - (dot['x'] - xc) * sin(teta) + (dot['y'] - yc) * cos(teta)
                dot['x'] = x_new
                dot['y'] = y_new
        self.paint()

    # возврат на шаг назад
    def back(self):
        # текущие и предыдущие точки обмениваются значениями
        tmp = deepcopy(self.elements_cur)
        self.elements_cur = deepcopy(self.elements_prev)
        self.elements_prev = deepcopy(tmp)
        # отрисовка
        self.paint()

    # вывод исходного изображения
    def again(self):
        # запоминаются предыдущие координаты
        self.elements_prev = deepcopy(self.elements_cur)
        # текущие точки инициализируются начальными
        self.elements_cur = deepcopy(self.elements_init)
        # отрисовка
        self.paint()


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MyWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':
    main()
