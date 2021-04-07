import design  # мой интерфейс
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QPen, QColor, QImage, QPixmap, QPainter
from PyQt5.QtCore import Qt, QTime, QEventLoop, QPointF
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
    elif color_name == 'Черный':
        return Qt.black


# для добаления точки по нажатию мышкой
class myScene(QtWidgets.QGraphicsScene):
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            w.add_point(event.scenePos())


# уравнение прямой по 2 точкам
def find_line_by_2points(x1, y1, x2, y2):
    # из уравнения прямой, проходящей через 2 точки
    # (x - x1)/ (x2 - x1) = (y - y1) / (y2 - y1)
    a = y2 - y1
    b = x1 - x2
    c = x2 * x1 - x1 * y2
    return a, b, c


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

        # цвета по умолчанию
        self.fill_color = Qt.green
        self.back_color = Qt.white

        # создание сцены
        self.scene = myScene(0, 0, 1600, 1250)
        self.scene.win = self
        self.graph.setScene(self.scene)
        # изображение
        self.image = QImage(1600, 1250, QImage.Format_ARGB32_Premultiplied)
        self.image.fill(self.back_color)

        self.edges = []  # список ребер многоугольника, ограничивающего заданную область
        self.point_start = None  # первая точка контура
        self.point_prev = None  # предыдущая точка
        self.pen = QPen(self.fill_color)  # цвет рисования

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
        self.point_start = None
        self.point_prev = None
        self.image.fill(self.back_color)

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
            self.get_fill_color()
            # выводим ребро на экран
            self.scene.addLine(round(self.point_prev.x()), round(self.point_prev.y()),
                               round(point.x()), round(point.y()), self.pen)
            self.point_prev = point

        # если фигура замкнулась
        if self.point_start == point:
            self.point_start = None
            self.point_prev = None

    # замыкание контура
    def on_bt_connect_clicked(self):
        if not self.point_start:
            self.handle_error("Ошибка", "Контур уже замкнут")
        elif len(self.edges) < 2 or self.on_one_line():
            self.handle_error("Ошибка", "Сначала введите не менее двух участков контура, "
                                        "не лежащих на одной прямой")
        else:
            self.add_point(self.point_start)

    # лежат ли все ребра контура на одной прямой
    def on_one_line(self):
        x_start = self.point_start.x()
        y_start = self.point_start.y()
        for i_start in range(len(self.edges)):
            ed = self.edges[i_start]
            if ed[0] == x_start and ed[1] == y_start:
                break
        for i in range(i_start, len(self.edges) - 1):
            ed1 = self.edges[i]
            for j in range(i + 1, len(self.edges)):
                ed2 = self.edges[j]
                if find_line_by_2points(*ed1) != find_line_by_2points(*ed2):
                    return False
        return True

    # заполнение
    def on_bt_fill_clicked(self):
        if self.point_start:
            self.handle_error('Предупреждение', 'Один из контуров остался незамкнутым.')
        self.get_fill_color()
        self.fill_polygon()

    # настройка цвета заполнения
    def get_fill_color(self):
        color_name = self.box_color.currentText()
        color_code = find_color_code(color_name)
        self.fill_color = color_code
        self.pen = QPen(self.fill_color)

    # вывод времени
    def display_time(self, time):
        self.lbl_time.setText("Время: {0:.3f}msc".format(time))

    # дополнение пикселя
    def invert_pixel(self, p, x, y):
        if QColor(self.image.pixel(x, y)) == self.back_color:
            p.setPen(QPen(self.fill_color))
        else:
            p.setPen(QPen(self.back_color))

    # нахождение абсциссы крайней правой вершины
    def find_max_x(self):
        x_max = self.edges[0][0]

        for i in range(len(self.edges)):
            if self.edges[i][0] > x_max:
                x_max = self.edges[i][0]

            if self.edges[i][2] > x_max:
                x_max = self.edges[i][2]

        return x_max

    # алгоритм заполнения "по ребрам"
    def fill_polygon(self):
        delay_flag = self.but_delay.isChecked()

        t = QTime()
        pix = QPixmap()  # отрисовываемая картинка
        p = QPainter()  # отрисовщик
        self.draw_edges(self.edges)
        p.begin(self.image)
        t.start()
        # находим абсциссу крайней правой вершины
        xm = self.find_max_x()

        # в цикле по ребрам
        for ed in self.edges:
            x1, y1 = ed[0], ed[1]
            x2, y2 = ed[2], ed[3]

            # Горизонтальные ребра не могут пересекать сканирующую строку и
            # игнорируются. Но при синтезе изображения они присутствуют,
            # так как формируются при отрисовке ребер.
            if y1 == y2:
                continue

            # рассматриваем ребро "сверху-вниз" в экранной СК
            if y1 > y2:
                y1, y2 = y2, y1
                x1, x2 = x2, x1

            cur_y = y1  # текущая сканирующая строка
            end_y = y2  # последняя сканирующая строка для данного ребра
            dx = (x2 - x1) / (y2 - y1)
            start_x = x1  # первый заполняемый пиксел первой сканирущей строки

            # в цикле по сканирующим строкам для данного ребра
            while cur_y <= end_y:
                # в цикле по пикселам сканирующей строки, расположенным
                # правее ее пересечения с ребром и левее крайней правой
                # вершины фигуры
                x = round(start_x)  # первый заполняемый пиксел текущей сканирущей строки
                while x < xm:
                    self.invert_pixel(p, x, cur_y)  # "дополняем" пиксел
                    p.drawPoint(x, cur_y)
                    x += 1
                # переходим к следующей сканирующей строке
                cur_y += 1
                start_x += dx

                # если выбрана опция "с задержкой",
                if delay_flag:
                    self.make_delay(pix)

        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)
        p.end()
        # вывод времени
        self.display_time(t.elapsed())

    # задержка
    def make_delay(self, pix):
        QtWidgets.QApplication.processEvents(QEventLoop.AllEvents, 1)
        pix.convertFromImage(self.image)
        self.scene.addPixmap(pix)

    # отрисовка ребер
    def draw_edges(self, edges):
        p = QPainter()
        p.begin(self.image)
        p.setPen(QPen(self.fill_color))
        # p.setPen(QPen(Qt.black))
        for e in edges:
            p.drawLine(e[0], e[1], e[2], e[3])
        p.end()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    w = MyWindow()  # Создаём объект класса ExampleApp
    w.show()  # Показываем окно
    sys.exit(app.exec_())  # и запускаем приложение


