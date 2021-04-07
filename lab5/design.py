# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2200, 1300)
        font = QtGui.QFont()
        font.setPointSize(12)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(20, 20, 441, 161))
        self.groupBox.setObjectName("groupBox")
        self.box_color = QtWidgets.QComboBox(self.groupBox)
        self.box_color.setGeometry(QtCore.QRect(10, 50, 391, 71))
        self.box_color.setObjectName("box_color")
        self.box_color.addItem("")
        self.box_color.addItem("")
        self.box_color.addItem("")
        self.box_color.addItem("")
        self.box_color.addItem("")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 200, 441, 101))
        self.groupBox_2.setObjectName("groupBox_2")
        self.but_delay = QtWidgets.QRadioButton(self.groupBox_2)
        self.but_delay.setGeometry(QtCore.QRect(20, 40, 351, 41))
        self.but_delay.setObjectName("but_delay")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 330, 441, 211))
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        self.label_3.setGeometry(QtCore.QRect(20, 60, 47, 41))
        self.label_3.setObjectName("label_3")
        self.box_y = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.box_y.setGeometry(QtCore.QRect(280, 60, 131, 41))
        self.box_y.setMinimum(-10000.0)
        self.box_y.setMaximum(10000.0)
        self.box_y.setSingleStep(100.0)
        self.box_y.setProperty("value", 100.0)
        self.box_y.setObjectName("box_y")
        self.box_x = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.box_x.setGeometry(QtCore.QRect(70, 60, 131, 41))
        self.box_x.setMinimum(-10000.0)
        self.box_x.setMaximum(10000.0)
        self.box_x.setSingleStep(100.0)
        self.box_x.setProperty("value", 100.0)
        self.box_x.setObjectName("box_x")
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(230, 60, 47, 41))
        self.label_4.setObjectName("label_4")
        self.but_add = QtWidgets.QPushButton(self.groupBox_3)
        self.but_add.setGeometry(QtCore.QRect(10, 140, 191, 41))
        self.but_add.setObjectName("but_add")
        self.graph = QtWidgets.QGraphicsView(self.centralwidget)
        self.graph.setGeometry(QtCore.QRect(530, 30, 1600, 1250))
        self.graph.setObjectName("graph")
        self.table = QtWidgets.QTableWidget(self.centralwidget)
        self.table.setGeometry(QtCore.QRect(40, 710, 411, 371))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.table.setFont(font)
        self.table.setObjectName("table")
        self.table.setColumnCount(2)
        self.table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(20, 670, 441, 421))
        self.groupBox_4.setObjectName("groupBox_4")
        self.but_fill = QtWidgets.QPushButton(self.centralwidget)
        self.but_fill.setGeometry(QtCore.QRect(30, 1130, 321, 61))
        self.but_fill.setObjectName("but_fill")
        self.but_clean = QtWidgets.QPushButton(self.centralwidget)
        self.but_clean.setGeometry(QtCore.QRect(30, 1220, 321, 61))
        self.but_clean.setObjectName("but_clean")
        self.lbl_time = QtWidgets.QLabel(self.centralwidget)
        self.lbl_time.setGeometry(QtCore.QRect(540, 1230, 771, 41))
        self.lbl_time.setObjectName("lbl_time")
        self.but_connect = QtWidgets.QPushButton(self.centralwidget)
        self.but_connect.setGeometry(QtCore.QRect(20, 580, 441, 61))
        self.but_connect.setObjectName("but_connect")
        self.groupBox_4.raise_()
        self.groupBox_2.raise_()
        self.groupBox.raise_()
        self.groupBox_3.raise_()
        self.graph.raise_()
        self.table.raise_()
        self.but_fill.raise_()
        self.but_clean.raise_()
        self.lbl_time.raise_()
        self.but_connect.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Алгоритм заполнения \"по ребрам\""))
        self.groupBox.setTitle(_translate("MainWindow", "Цвет заполнения"))
        self.box_color.setItemText(0, _translate("MainWindow", "Зеленый"))
        self.box_color.setItemText(1, _translate("MainWindow", "Красный"))
        self.box_color.setItemText(2, _translate("MainWindow", "Черный"))
        self.box_color.setItemText(3, _translate("MainWindow", "Синий"))
        self.box_color.setItemText(4, _translate("MainWindow", "Желтый"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Режим"))
        self.but_delay.setText(_translate("MainWindow", "С задержкой"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Добавление точки"))
        self.label_3.setText(_translate("MainWindow", "X:"))
        self.label_4.setText(_translate("MainWindow", "Y:"))
        self.but_add.setText(_translate("MainWindow", "Добавить"))
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "X"))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Y"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Введенные точки"))
        self.but_fill.setText(_translate("MainWindow", "Закрасить фигуру"))
        self.but_clean.setText(_translate("MainWindow", "Очистить экран"))
        self.lbl_time.setText(_translate("MainWindow", "Время:"))
        self.but_connect.setText(_translate("MainWindow", "Замнкнуть контур"))
