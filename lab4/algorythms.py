from numpy import sign, sqrt, pi, sin, cos
import numpy as np


# симметричное отражение 1/8 плоскости
def mirror_8(dots, xc, yc, color, x, y):
    dots.extend([
        [x, y, color],
        [xc - (x - xc), y, color],
        [x, yc - (y - yc), color],
        [xc - (x - xc), yc - (y - yc), color],
        [y + xc - yc, x + yc - xc, color],
        [xc - y + yc, x + yc - xc, color],
        [y + xc - yc, yc - x + xc, color],
        [xc - y + yc, yc - x + xc, color]
    ])


# симметричное отражение 1/4 плоскости
def mirror_4(dots, xc, yc, color, x, y):
    dots.extend([
        [x, y, color],
        [xc - (x - xc), y, color],
        [x, yc - (y - yc), color],
        [xc - (x - xc), yc - (y - yc), color]
    ])


# построение окружности по каноническому уравнению
# (x-xc)**2 + (y-yc)**2 = r**2
def circle_canonical(xc, yc, r, color):
    xc, yc = round(xc), round(yc)
    dots = []

    # находим точки 1/8 части окружности
    # аргумент - x, приращение 1
    for x in range(xc, xc + int(r / sqrt(2)) + 1):
        y = round(sqrt(r ** 2 - (x - xc) ** 2)) + yc
        # отражаем относительно ox, oy и 2 биссектрис
        mirror_8(dots, xc, yc, color, x, y)

    return dots


# построение окружности по параметрическому уравнению
# x = xc + r*cos(t)
# y = yc + r*sin(t)
def circle_parametric(xc, yc, r, color):
    dots = []
    # минимальный шаг изменения угла t = 1 / r, т.к. расстояние между пикселямми пропорционально
    # углу между ними (вершина угла в центре окружности)
    step = 1 / r

    # находим точки 1/8 части окружности
    for t in np.arange(0, pi / 4 + step, step):
        x = round(xc + r * cos(t))
        y = round(yc + r * sin(t))
        # отражаем относительно ox, oy и 2 биссектрис
        mirror_8(dots, xc, yc, color, x, y)

    return dots


# построение окружности по алгоритму Брезенхема
# строится окружность указанного радиуса с центром в (0, 0),
# а в массив записываются координаты с учетом смещения на (xc, yc)
def circle_brezenham(xc, yc, r, color):
    dots = []

    # начальные значения
    x = 0
    y = round(r)
    # разность квадратов расстояний от центра окружности до диагонального
    # (xi + 1,yi - 1) пикселя и до идеальной окружности
    delta = 2 * (1 - r)

    mirror_8(dots, xc, yc, color, x + xc, y + xc)

    # находим точки 1/8 части окружности
    while x < y:
        # горизонтальный или диагональный (1, 2, 5 случаи)
        if delta <= 0:
            # смещаемся вправо
            delta_tmp = 2 * (delta + y) - 1
            x += 1
            # диагональный
            if delta_tmp >= 0:
                delta += 2 * (x - y + 1)
                y -= 1
            # горизонтальный
            else:
                delta += 2 * x + 1
        # вертикальный или диагональнй (3, 4 случаи)
        else:
            # смещаемся вниз
            delta_tmp = 2 * (delta - x) - 1
            y -= 1
            # диагональный
            if delta_tmp < 0:
                delta += 2 * (x - y + 1)
                x += 1
            # вертикальный
            else:
                delta -= 2 * y - 1
        # отражаем относительно ox, oy и 2 биссектрис
        mirror_8(dots, xc, yc, color, x + xc, y + xc)

    return dots


# построение окружности по алгоритму средней точки
# строится окружность указанного радиуса с центром в (0, 0),
# а в массив записываются координаты с учетом смещения на (xc, yc)
def circle_midpoint(xc, yc, r, color):
    r_sqr = r * r
    r_sqr_2 = r_sqr * 2

    # начальные значения
    dots = []
    x = 0
    y = round(r)
    delta = r_sqr - r_sqr * r + 0.25 * r_sqr
    dx = r_sqr_2 * x
    dy = r_sqr_2 * y

    # находим точки 1/8 части окружности
    while dx < dy:
        # отражаем относительно ox, oy и 2 биссектрис
        mirror_8(dots, xc, yc, color, x + xc, y + yc)
        x += 1
        dx += r_sqr_2
        # средняя точка вне окружности - выбираем нижнюю
        if delta >= 0:
            y -= 1
            # корректируем дельту
            dy -= r_sqr_2
            delta -= dy
        delta += dx + r_sqr

    return dots


# построение эллипса по каноническому уравнению
# (x-xc)**2 / a ** 2 + (y-yc)**2 / b ** 2 = 1
def ellipse_canonical(xc, yc, a, b, color):
    xc, yc = round(xc), round(yc)
    dots = []
    a_sqr = a * a
    b_sqr = b * b
    a_b_sqr = a_sqr * b_sqr

    x_limit = int(xc + a / sqrt(1 + b_sqr / a_sqr))
    y_limit = int(yc + b / sqrt(1 + a_sqr / b_sqr))

    # строим 1/4 эллипса
    # 1 участок
    for x in range(xc, x_limit + 1):
        y = round(sqrt(a_b_sqr - (x - xc) ** 2 * b_sqr) / a) + yc
        # отражаем относительно ox и oy
        mirror_4(dots, xc, yc, color, x, y)

    # 2 участок
    for y in range(y_limit, yc - 1, -1):
        x = round(sqrt(a_b_sqr - (y - yc) ** 2 * a_sqr) / b) + xc
        # отражаем относительно ox и oy
        mirror_4(dots, xc, yc, color, x, y)

    return dots


# построение эллипса по параметрическому уравнению
# x = xc + a*cos(t)
# y = yc + b*sin(t)
def ellipse_parametric(xc, yc, a, b, color):
    dots = []
    # минимальный шаг изменения угла t = 1 / max(a, b), т.к. расстояние между пикселямми пропорционально
    # углу между ними (вершина угла в центре эллипса)
    step = 1 / a if a > b else 1 / b

    # строим 1/4 эллипса
    for t in np.arange(0, pi / 2 + step, step):
        x = round(xc + a * cos(t))
        y = round(yc + b * sin(t))
        # отражаем относительно ox, oy
        mirror_4(dots, xc, yc, color, x, y)

    return dots


# построение эллипса по алгоритму Брезенхема
# строится эллипс с центром в (0, 0),
# а в массив записываются координаты с учетом смещения на (xc, yc)
def ellipse_brezenham(xc, yc, a, b, color):
    dots = []
    a_sqr = a * a
    b_sqr = b * b

    # начальные значения
    x = 0
    y = round(b)
    # разность квадратов расстояний от центра эллипса до диагонального
    # (xi + 1,yi - 1) пикселя и до идеального эллипса
    delta = b_sqr - a_sqr * (2 * b - 1) ## в конце +

    mirror_4(dots, xc, yc, color, x + xc, y + yc)

    # строим 1/4 эллипса
    while y > 0:
        # горизонтальный или диагональный (1, 2, 5 случаи)
        if delta <= 0:
            # смещаемся вправо
            delta_temp = 2 * delta + a_sqr * (2 * y - 1)
            x += 1

            # диагональный
            if delta_temp >= 0:
                # смещаемся вниз
                y -= 1
                delta += 2 * (b_sqr * x - a_sqr * y) + b_sqr + a_sqr
            # горизонтальный
            else:
                delta += b_sqr * 2 * x + b_sqr
        # вертикальный или диагональный (3 и 4 случаи)
        else:
            # смещаемся вниз
            delta_temp = 2 * delta + b_sqr * (-2 * x - 1)
            y -= 1
            # диагональный
            if delta_temp < 0:
                # смещаемся вправо
                x += 1
                delta += 2 * (b_sqr * x - a_sqr * y) + b_sqr + a_sqr
            # вертикальный
            else:
                delta += -a_sqr * 2 * y + a_sqr

        # отражаем относительно ox и oy
        mirror_4(dots, xc, yc, color, x + xc, y + yc)

    return dots


# построение эллипса по алгоритму средней точки
# строится эллипс с центром в (0, 0),
# а в массив записываются координаты с учетом смещения на (xc, yc)
def ellipse_midpoint(xc, yc, a, b, color):
    a_sqr = a * a
    b_sqr = b * b
    a_b_sqr = a_sqr * b_sqr
    a_sqr_2 = a_sqr * 2
    b_sqr_2 = b_sqr * 2

    # начальные значения
    dots = []
    x = 0
    y = b
    delta = b_sqr - a_sqr * b + 0.25 * a_sqr
    dx = b_sqr_2 * x
    dy = a_sqr_2 * y

    # находим точки 1/4 части окружности
    # первый участок - x аргумент
    while dx < dy:
        # отражаем относительно ox и oy
        mirror_4(dots, xc, yc, color, x + xc, y + yc)
        x += 1
        dx += b_sqr_2
        # средняя точка вне эллипса - выбираем нижнюю
        if delta >= 0:
            y -= 1
            # корректируем дельту
            dy -= a_sqr_2
            delta -= dy
        delta += dx + b_sqr

    # корректируем дельту при переходе на второй участок
    delta = b_sqr * (x + 0.5) ** 2 + a_sqr * (y - 1) ** 2 - a_b_sqr

    # второй участок - y аргумент
    while y >= 0:
        # отражаем относительно ox и oy
        mirror_4(dots, xc, yc, color, x + xc, y + yc)

        y -= 1
        dy -= a_sqr_2
        # средняя точка вне эллипса - выбираем правую
        if delta <= 0:
            x += 1
            # корректируем дельту
            dx += b_sqr_2
            delta += dx

        delta -= dy - a_sqr

    return dots


def circle_lib(xc, yc, r, color):
    return ['lib', xc - r, yc - r, 2 * r, 2 * r, color]


def ellipse_lib(xc, yc, a, b, color):
    return ['lib', xc - a, yc - b, 2 * a, 2 * b, color]
