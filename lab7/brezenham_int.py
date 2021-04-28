from numpy import sign


def bresenham_int(x1, y1, x2, y2):
    points = []
    # Вычисление приращений.
    dx = x2 - x1
    dy = y2 - y1
    # Вычисление шага изменение каждой координаты пикселя
    s_x = sign(dx)
    s_y = sign(dy)
    # Вычисление модуля приращения.
    dx = abs(dx)
    dy = abs(dy)
    # Обмен местами координат в случае m > 1 (тангенс)
    if dy >= dx:
        dx, dy = dy, dx
        change = 1
    else:
        change = 0
    # Иницилизация начального значения ошибки.
    m = 2 * dy  # в случае FLOAT m = dy / dx
    m1 = 2 * dx
    e = m - dx  # в случае FLOAT e = m - 0.5
    # Инициализации начальных значений текущего пикселя
    # (т е начало отрезка тут)
    x = round(x1)
    y = round(y1)
    # Цикл от i = 1 до i = dx + 1 с шагом 1
    i = 1
    while i <= dx + 1:
        points.append([x, y])
        if e >= 0:
            if change == 1:
                x += s_x
            else:
                y += s_y
            e -= m1  # в случае FLOAT e -= 1
        if e <= 0:
            if change == 1:
                y += s_y
            else:
                x += s_x
            e += m
        i += 1

    return points