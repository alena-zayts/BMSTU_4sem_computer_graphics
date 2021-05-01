import design  # мой интерфейс
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QPen, QColor, QImage, QPixmap, QPainter
from PyQt5.QtCore import Qt, QTime, QEventLoop, QPointF
from brezenham_int import bresenham_int
from midpoint_cut import midpoint_cut
import sys

global w
EPS = 1e-6


# код цвета по названию
def find_color_code(color_name):
    if color_name == 'Красный':
        return Qt.red
    elif color_name == 'Зеленый':
        return Qt.green
    elif color_name == 'Синий':
        return Qt.darkBlue
    elif color_name == 'Желтый':
        return Qt.yellow
    elif color_name == 'Голубой':
        return Qt.blue
    elif color_name == 'Бирюзовый':
        return Qt.cyan
    elif color_name == 'Розовый':
        return Qt.magenta
    elif color_name == 'Черный':
        return Qt.black


# для добаления точки по нажатию мышкой
class myScene(QtWidgets.QGraphicsScene):
    def mousePressEvent(self, event):
        point = [round(event.scenePos().x()), round(event.scenePos().y())]
        if event.buttons() == Qt.LeftButton:
            w.add_segment_point(point)
        if event.buttons() == Qt.RightButton:
            w.add_cutter_point(point)
        if event.buttons() == Qt.MidButton:
            w.add_segment_point_aligned(point)

    # def mouseMoveEvent(self, event):
    #     self.mousePressEvent(event)


class MyWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # для доступа к переменным, методам и т.д. в файле design.py
        super().__init__()
        # инициализация дизайна
        self.setupUi(self)
        # настройка кнопок
        self.but_clean.clicked.connect(self.on_bt_clean_clicked)
        self.but_input_cutter.clicked.connect(self.on_bt_input_cutter_clicked)
        self.but_connect.clicked.connect(self.on_bt_connect_clicked)
        self.but_input_point.clicked.connect(self.on_bt_input_point_clicked)
        self.but_cut.clicked.connect(self.on_bt_cut_clicked)

        self.color_back = Qt.white
        self.color_cutter = None
        self.color_segment = None
        self.color_result = None

        self.cutter = []
        self.cutter_start = None
        self.cutter_prev = None
        self.cutter_tmp = []
        self.segments = []
        self.segment_prev = None
        self.eps = None

        # создание сцены
        self.scene = myScene(0, 0, 1600, 1100)
        self.scene.win = self
        self.graph.setScene(self.scene)
        # изображение
        self.image = QImage(1600, 1100, QImage.Format_ARGB32_Premultiplied)
        self.image.fill(self.color_back)

    # обработка ошибки
    def handle_error(self, title, error):
        em = QtWidgets.QMessageBox(self.centralwidget)
        em.setText(error)
        em.setWindowTitle(title)
        em.exec()

    # очистка экрана и данных
    def on_bt_clean_clicked(self):
        for i in range(self.table.rowCount(), -1, -1):
            self.table.removeRow(i)
        self.scene.clear()
        self.table.clearContents()
        self.image.fill(self.color_back)
        self.lbl_cutter.clear()

        self.color_back = Qt.white
        self.color_cutter = None
        self.color_segment = None
        self.color_result = None

        self.cutter = []
        self.cutter_start = None
        self.cutter_prev = None
        self.cutter_tmp = []
        self.segments = []
        self.segment_prev = None
        self.eps = None

    # # ввод точности
    # def on_bt_input_eps_clicked(self):
    #     self.eps = self.box_eps.value()

    # добавление строки в таблицу
    def add_row_to_table(self):
        self.table.insertRow(self.table.rowCount())

    # настройка цвета отсекателя
    def get_color_cutter(self):
        color_name = self.box_color_cutter.currentText()
        color_code = find_color_code(color_name)
        self.color_cutter = color_code

    # настройка цвета отрезков
    def get_color_segment(self):
        color_name = self.box_color_segment.currentText()
        color_code = find_color_code(color_name)
        self.color_segment = color_code

    # настройка цвета результата
    def get_color_result(self):
        color_name = self.box_color_result.currentText()
        color_code = find_color_code(color_name)
        self.color_result = color_code

    # общий алгоритм добавления вершины отрезка
    def add_segment_point(self, point):
        self.get_color_segment()
        if not self.segment_prev:
            self.draw_segments([[point[0], point[1], point[0], point[1], self.color_segment]])
            self.segment_prev = point
            # добавление в таблицу
            i = self.table.rowCount()
            self.add_row_to_table()
            x1 = QTableWidgetItem("{}".format(self.segment_prev[0]))
            y1 = QTableWidgetItem("{}".format(self.segment_prev[1]))
            self.table.setItem(i, 0, x1)
            self.table.setItem(i, 1, y1)
        else:
            self.draw_segments([[self.segment_prev[0], self.segment_prev[1], point[0], point[1], self.color_segment]])
            self.segments.append([self.segment_prev[0], self.segment_prev[1], point[0], point[1], self.color_segment])
            # добавление в таблицу
            i = self.table.rowCount()
            x2 = QTableWidgetItem("{}".format(point[0]))
            y2 = QTableWidgetItem("{}".format(point[1]))
            self.table.setItem(i - 1, 2, x2)
            self.table.setItem(i - 1, 3, y2)
            self.segment_prev = None

    # добавление вершины отрезка по кнопке
    def on_bt_input_point_clicked(self):
        self.add_segment_point([self.box_xo.value(), self.box_yo.value()])

    # добавление вершины отрезка c выравниванием
    def add_segment_point_aligned(self, point):
        if not self.segment_prev:
            self.add_segment_point(point)
        else:
            distance_x = abs(self.segment_prev[0] - point[0])
            distance_y = abs(self.segment_prev[1] - point[1])
            if distance_x < distance_y:
                self.add_segment_point([self.segment_prev[0], point[1]])
            else:
                self.add_segment_point([point[0], self.segment_prev[1]])

    # отрисовка исходных отрезков
    def draw_segments(self, segments):
        p = QPainter()
        p.begin(self.image)
        for segment in segments:
            p.setPen(QPen(segment[-1]))
            self.my_darw_line(p, segment[:-1])
        p.end()

        pix = QPixmap()  # отрисовываемая картинка
        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)

    # добваление отсекателя по кнопке
    def on_bt_input_cutter_clicked(self):
        if self.cutter:
            self.handle_error('Ошибка.', 'Отсекатель уже введен')
            return
        if self.cutter_start:
            self.handle_error('Ошибка.', 'Отсекатель уже вводится мышью')
            return
        self.get_color_cutter()
        self.cutter = [self.box_xl.value(), self.box_xr.value(),
                       self.box_yl.value(), self.box_yu.value()]
        self.draw_cutter(self.cutter)
        self.print_cutter()

    # добавление вершины отсекателя
    def add_cutter_point(self, point):
        if self.cutter:
            self.handle_error('Ошибка.', 'Отсекатель уже введен')
            return
        if not self.cutter_start:
            self.get_color_cutter()
            self.cutter_start = point
            self.cutter_prev = point
            self.cutter_tmp.append(point)
            self.draw_cutter([point[0], point[0], point[1], point[1]])
            return
        if (point[0] == self.cutter_start[0]) and (point[1] == self.cutter_start[1]):
            self.form_cutter()
            self.draw_cutter(self.cutter)
            self.cutter_start = None
            self.print_cutter()
            return

        distance_x = abs(self.cutter_prev[0] - point[0])
        distance_y = abs(self.cutter_prev[1] - point[1])
        if distance_x < distance_y:
            if point[1] < self.cutter_start[1]:
                self.handle_error('Ошибка.', 'Некорректный ввод отсекателя. Обратите '
                                             'внимание: отсекатель вводится с левой верхней вершины.')
                return
            if (len(self.cutter_tmp) > 1) and \
                    (self.cutter_tmp[-1][0] == self.cutter_tmp[-2][0]):
                self.cutter_tmp.pop()
            if len(self.cutter_tmp) == 4:
                self.add_cutter_point(self.cutter_start)
                return
            self.cutter_tmp.append([self.cutter_prev[0], point[1]])
            self.cutter_prev = [self.cutter_prev[0], point[1]]
        else:
            if point[0] < self.cutter_start[0]:
                self.handle_error('Ошибка.', 'Некорректный ввод отсекателя. Обратите '
                                             'внимание: отсекатель вводится с левой верхней вершины.')
                return
            if (len(self.cutter_tmp) > 1) and \
                    (self.cutter_tmp[-1][1] == self.cutter_tmp[-2][1]):
                self.cutter_tmp.pop()
            if len(self.cutter_tmp) == 4:
                self.add_cutter_point(self.cutter_start)
                return
            self.cutter_tmp.append([point[0], self.cutter_prev[1]])
            self.cutter_prev = [point[0], self.cutter_prev[1]]
        self.draw_cutter_part()

    def form_cutter(self):
        xl = self.cutter_start[0]
        xr = self.cutter_start[0]
        yl = self.cutter_start[1]
        yu = self.cutter_start[1]
        for point in self.cutter_tmp:
            if point[0] < xl:
                xl = point[0]
            elif point[0] > xr:
                xr = point[0]
            if point[1] < yu:
                yu = point[1]
            elif point[1] > yl:
                yl = point[1]
        self.cutter = [xl, xr, yl, yu]

    # вывод отсекателя в текстовое поле
    def print_cutter(self):
        text = "xл: %d    xп: %d\n" \
               "yв: %d    yн: %d" % \
               (self.cutter[0], self.cutter[1], self.cutter[3], self.cutter[2])
        self.lbl_cutter.setText(text)

    # отрисовка части отсекателя
    def draw_cutter_part(self):
        p = QPainter()
        p.begin(self.image)
        p.setPen(QPen(self.color_cutter))
        for i in range(len(self.cutter_tmp) - 1):
            segment = [self.cutter_tmp[i][0], self.cutter_tmp[i][1],
                       self.cutter_tmp[i + 1][0], self.cutter_tmp[i + 1][1]]
            self.my_darw_line(p, segment)
        p.end()

        pix = QPixmap()  # отрисовываемая картинка
        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)

    # отрисовка отсекателя
    def draw_cutter(self, cutter):
        p = QPainter()
        p.begin(self.image)
        p.setPen(QPen(self.color_cutter))
        xl = cutter[0]
        xr = cutter[1]
        yl = cutter[2]
        yu = cutter[3]
        lines = [[xl, yu, xr, yu], [xl, yl, xr, yl], [xl, yu, xl, yl], [xr, yu, xr, yl]]
        for line in lines:
            self.my_darw_line(p, line)
        p.end()

        pix = QPixmap()  # отрисовываемая картинка
        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)

    # замыкание контура отсекателя
    def on_bt_connect_clicked(self):
        if not self.cutter_start:
            self.handle_error("Ошибка", "Отсекатель уже замкнут или не было введено ни одной точки")
        else:
            self.add_cutter_point(self.cutter_start)

    def my_repaint(self):
        self.image.fill(self.color_back)
        self.draw_segments(self.segments)
        self.draw_cutter(self.cutter)

    # рисование отрезка
    def my_darw_line(self, p, segment):
        p.drawLine(*segment)
        # points = bresenham_int(*segment)
        # for point in points:
        #     p.drawPoint(*point)

    # отсечение
    def on_bt_cut_clicked(self):
        if not self.cutter:
            self.handle_error("Ошибка", "Сначала введите отсекатель")
            return
        eps = 2 ** 0.5
        width = self.box_width.value()
        self.get_color_result()

        if self.segment_prev:
            self.segments.append([self.segment_prev[0], self.segment_prev[1],
                                 self.segment_prev[0], self.segment_prev[1], self.color_segment])

        self.my_repaint()
        p = QPainter()
        p.begin(self.image)
        p.fillRect(self.cutter[0] + 1, self.cutter[3] + 1,
                   self.cutter[1] - self.cutter[0] - 2,
                   self.cutter[2] - self.cutter[3] - 2, self.color_back)
        p.setPen(QPen(self.color_result, width))
        for segment in self.segments:
            p1 = [segment[0], segment[1]]
            p2 = [segment[2], segment[3]]
            segment_cut = midpoint_cut(self.cutter, p1, p2, eps)
            if segment_cut:
                self.my_darw_line(p, segment_cut)

        p.end()
        pix = QPixmap()  # отрисовываемая картинка
        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    w = MyWindow()  # Создаём объект класса ExampleApp
    w.show()  # Показываем окно
    sys.exit(app.exec_())  # и запускаем приложение
