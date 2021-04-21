import design  # мой интерфейс
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QPen, QColor, QImage, QPixmap, QPainter
from PyQt5.QtCore import Qt, QTime, QEventLoop, QPointF
from brezenham_int import bresenham_int
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
        if event.buttons() == Qt.LeftButton:
            w.add_point(event.scenePos())
        if event.buttons() == Qt.RightButton:
            w.add_seedp(event.scenePos())

    def mouseMoveEvent(self, event):
        self.mousePressEvent(event)


class MyWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # для доступа к переменным, методам и т.д. в файле design.py
        super().__init__()
        # инициализация дизайна
        self.setupUi(self)
        # настройка кнопок
        self.but_fill.clicked.connect(self.on_bt_fill_clicked)
        self.but_clean.clicked.connect(self.on_bt_clean_clicked)
        self.but_add.clicked.connect(self.on_bt_add_clicked)
        self.but_connect.clicked.connect(self.on_bt_connect_clicked)
        self.but_seed.clicked.connect(self.on_bt_seed_clicked)

        self.back_color = Qt.white

        # создание сцены
        self.scene = myScene(0, 0, 1600, 1270)
        self.scene.win = self
        self.graph.setScene(self.scene)
        # изображение
        self.image = QImage(1600, 1270, QImage.Format_ARGB32_Premultiplied)
        self.image.fill(self.back_color)

        self.edges = []  # список ребер многоугольника, ограничивающего заданную область
        self.point_start = None  # первая точка контура
        self.point_prev = None  # предыдущая точка
        self.seedp = None

        self.stack = []

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
        self.edges = []
        self.seedp = None
        self.point_start = None
        self.point_prev = None
        self.image.fill(self.back_color)
        self.fill_color = None
        self.border_color = None

    # добавление затравочной точки по кнопке
    def on_bt_seed_clicked(self):
        p = QPointF()
        p.setX(self.box_x.value())
        p.setY(self.box_y.value())
        self.add_seedp(p)

    # общий алгоритм добаления затравочной точки
    def add_seedp(self, point):
        if self.seedp:
            self.handle_error('Ошибка', 'Уже введена затравочная точка с координатами'
                                        ' (%d, %d)'%(self.seedp[0], self.seedp[1]))
            return
        self.seedp = [round(point.x()), round(point.y())]
        # добавление в таблицу
        i = self.table.rowCount()
        self.add_row_to_table()
        x = QTableWidgetItem("{}".format(point.x()))
        y = QTableWidgetItem("{}".format(point.y()))
        m = QTableWidgetItem("затравочная")
        self.table.setItem(i, 0, x)
        self.table.setItem(i, 1, y)
        self.table.setItem(i, 2, m)
        # получаем цвет закраски только 1 раз!
        self.get_fill_color()

    # добавление точки по нажатию кнопки
    def on_bt_add_clicked(self):
        p = QPointF()
        p.setX(self.box_x.value())
        p.setY(self.box_y.value())
        self.add_point(p)

    # добавление строки в таблицу
    def add_row_to_table(self):
        self.table.insertRow(self.table.rowCount())

    # общий алгоритм добаления точки
    def add_point(self, point):
        # получаем цвет границы только 1 раз!
        if (not self.edges) and (not self.point_start):
            self.get_border_color()
        # добавление в таблицу
        i = self.table.rowCount()
        self.add_row_to_table()
        x = QTableWidgetItem("{}".format(point.x()))
        y = QTableWidgetItem("{}".format(point.y()))
        self.table.setItem(i, 0, x)
        self.table.setItem(i, 1, y)

        # если точка - начало контура
        if not self.point_start:
            self.point_start = point
            self.point_prev = point
            return

        # если точка не совпала с предыдущей:
        elif self.point_prev != point:
            # в ребрах хранятся только целые координаты вершин
            self.edges.append([round(self.point_prev.x()), round(self.point_prev.y()),
                               round(point.x()), round(point.y())])
            # выводим ребро на экран
            self.draw_edges([[round(self.point_prev.x()), round(self.point_prev.y()),
                             round(point.x()), round(point.y())]])
            self.point_prev = point

        # если фигура замкнулась
        if self.point_start == point:
            self.point_start = None
            self.point_prev = None

    # замыкание контура
    def on_bt_connect_clicked(self):
        if not self.point_start:
            self.handle_error("Ошибка", "Контур уже замкнут")
        else:
            self.add_point(self.point_start)

    # заполнение
    def on_bt_fill_clicked(self):
        if self.edges == []:
            self.handle_error('Ошибка', 'Введите границы заполняемой области')
            return

        if self.point_start:
            self.handle_error('Ошибка', 'Один из контуров остался незамкнутым.')
            return

        if not self.seedp:
            self.handle_error('Ошибка', 'Введите затравочную точку.')
            return

        # self.draw_edges(self.edges)
        ########## нужно ли
        # self.draw_edges([[0, 0, 1600, 0], [1600, 0, 1600, 1270], [1600, 1270, 0, 1270], [0, 1270, 0, 0]])
        self.fill_polygon()

    # настройка цвета заполнения
    def get_fill_color(self):
        color_name = self.box_color.currentText()
        color_code = find_color_code(color_name)
        self.fill_color = color_code

    # настройка цвета границы
    def get_border_color(self):
        color_name = self.box_color_border.currentText()
        color_code = find_color_code(color_name)
        self.border_color = color_code

    # вывод времени
    def display_time(self, time):
        self.lbl_time.setText("Время: {0:.0f}msc".format(time))

    # задержка
    def make_delay(self, pix):
        QtWidgets.QApplication.processEvents(QEventLoop.AllEvents, 1)
        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)

    # отрисовка ребер
    def draw_edges(self, edges):
        p = QPainter()
        p.begin(self.image)
        p.setPen(QPen(self.border_color))
        for e in edges:
            points = bresenham_int(*e)
            for point in points:
                p.drawPoint(*point)
        p.end()

        pix = QPixmap()  # отрисовываемая картинка
        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)

    # получение цвета пиксела
    def get_color(self, x, y):
        return QColor(self.image.pixel(x, y))

    # установка цвета пиксела
    def set_color(self, x, y, color, p):
        p.setPen(QPen(color))
        p.drawPoint(x, y)

    # построчный алгоритм заполнения гранично-определенной области с затравкой
    def fill_polygon(self):
        delay_flag = self.but_delay.isChecked()
        if delay_flag:
            delay_lvl = self.delay_lvl.maximum() - self.delay_lvl.value() + 1
        cur_count = 0  # для отслеживания задержки

        t = QTime()
        pix = QPixmap()  # отрисовываемая картинка
        p = QPainter()  # отрисовщик
        p.begin(self.image)
        t.start()

        # Занесение в стек затравочного пиксела
        stack = [self.seedp]

        # пока стек не пуст
        while stack:
            # извлекаем очередной затравочный пиксел
            point = stack.pop()
            x, y = point[0], point[1]

            # заполняем интервал вправо от затравки (включая затравку)
            # и запоминаем крайний правый пиксел
            x_cur = x
            while self.get_color(x_cur, y) != self.border_color:
                self.set_color(x_cur, y, self.fill_color, p)
                x_cur += 1
            xr = x_cur - 1

            # заполняем интервал влево от затравки (не включая затравку)
            # и запоминаем крайний левый пиксель
            x_cur = x - 1
            while self.get_color(x_cur, y) != self.border_color:
                self.set_color(x_cur, y, self.fill_color, p)
                x_cur -= 1
            xl = x_cur + 1
            # Поиск новых затравочных пикселей в интервале xl <= x <= xr на двух соседних строках y+1, y-1
            for y_ in [y + 1, y - 1]:
                x = xl
                while x <= xr:
                    # флаг перехождения затравки
                    flag = 0
                    # ищем (хоть один или крайний правый) затравочный пиксель
                    while ((self.get_color(x, y_) != self.border_color) and
                           (self.get_color(x, y_) != self.fill_color) and
                           (x <= xr)):                                                      ###
                        flag = 1
                        x += 1
                    # если такой нашелся, то помещаем его в стек
                    if flag:
                        # дошли до конца интервала
                        if ((self.get_color(x, y_) != self.border_color) and
                           (self.get_color(x, y_) != self.fill_color) and
                           (x == xr)):
                            stack.append([x, y_])
                        # встретили границу или уже заполненную часть на интервале
                        else:
                            stack.append([x - 1, y_])

                    # Поиск нового интервала в случае прерывания текущего интервала (произойдет, если  x<xr)
                    # запоминаем абсциссу текущего пиксела
                    xn = x
                    # flag = 0
                    while (((self.get_color(x, y_) == self.border_color) or
                           (self.get_color(x, y_) == self.fill_color)) and
                           (x < xr)):
                        x += 1
                    # убедимся, что координата абсциссы пикселя увеличилась (чтобы не зациклиться)
                    if x == xn:
                        x += 1
            # если выбрана опция "с задержкой",
            if delay_flag:
                cur_count += 1
                if cur_count == delay_lvl:
                    self.make_delay(pix)
                    cur_count = 0

        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)
        p.end()
        # вывод времени
        self.display_time(t.elapsed())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    w = MyWindow()  # Создаём объект класса ExampleApp
    w.show()  # Показываем окно
    sys.exit(app.exec_())  # и запускаем приложение
