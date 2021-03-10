from numpy import sign


def change_color_intensity(color, intensity):
    return tuple(((1 - intensity) * 255) if elem != 255 else 255
                 for elem in color)


# цифровой дифференциальный анализатор
def dda(xn, yn, xk, yk, color):
    if abs(xk - xn) > abs(yk - yn):
        length = abs(xk - xn)
    else:
        length = abs(yk - yn)

    dx = (xk - xn) / length
    dy = (yk - yn) / length

    # начало основного цикла
    x = xn
    y = yn
    dots = []
    for i in range(round(length) + 1):
        dots.append([round(x), round(y), color])
        x = x + dx
        y = y + dy

    return dots


# x, y, dx, dy - целые
# e - вещественное
# концы отрезка не совпадают
def brezenham_float(xn, yn, xk, yk, color):
    xn = round(xn)
    xk = round(xk)
    yn = round(yn)
    yk = round(yk)

    dx = xk - xn
    dy = yk - yn
    signx = sign(dx)
    signy = sign(dy)
    dx = abs(dx)
    dy = abs(dy)

    # обмен значений dx и dy в зависимости от углового коэффициента
    if dy > dx:
        change_flag = True
        dx, dy = dy, dx
    else:
        change_flag = False

    # угловой коэффициент
    m = dy / dx

    # инициализация начального приближения ошибки
    e = m - 0.5

    # начало основного цикла
    x = xn
    y = yn
    dots = []
    for i in range(dx + 1):
        dots.append([x, y, color])
        while e >= 0:
            if change_flag:
                x += signx
            else:
                y += signy
            e -= 1
        if change_flag:
            y += signy
        else:
            x += signx
        e += m

    return dots


# все переменные целые
# концы отрезка не совпадают
def brezenham_int(xn, yn, xk, yk, color):
    xn = round(xn)
    xk = round(xk)
    yn = round(yn)
    yk = round(yk)

    dx = xk - xn
    dy = yk - yn
    signx = sign(dx)
    signy = sign(dy)
    dx = abs(dx)
    dy = abs(dy)

    # обмен значений dx и dy в зависимости от углового коэффициента
    if dy > dx:
        change_flag = True
        dx, dy = dy, dx
    else:
        change_flag = False

    # инициализация e с поправкой на половину пиксела
    e = 2 * dy - dx
    dx_mul2 = 2 * dx
    dy_mul2 = 2 * dy

    # начало основного цикла
    x = xn
    y = yn
    dots = []
    for i in range(dx + 1):
        dots.append([x, y, color])
        while e >= 0:
            if change_flag:
                x += signx
            else:
                y += signy
            e -= dx_mul2
        if change_flag:
            y += signy
        else:
            x += signx
        e += dy_mul2

    return dots


def brezenham_del_stag(xn, yn, xk, yk, color):
    xn = round(xn)
    xk = round(xk)
    yn = round(yn)
    yk = round(yk)

    dx = xk - xn
    dy = yk - yn
    signx = sign(dx)
    signy = sign(dy)
    dx = abs(dx)
    dy = abs(dy)

    # обмен значений dx и dy в зависимости от углового коэффициента
    if dy > dx:
        change_flag = True
        dx, dy = dy, dx
    else:
        change_flag = False

    # угловой коэффициент
    m = dy / dx

    # инициализация e (ошибка - это мера площади той части
    # пиксела, которая находится внутри многоугольника
    # для первого пиксела алгоритм всегда будет выдавать значение
    # интенсивности, равное половине максимальной.
    e = 1 / 2

    # величина w = 1 - m, позволяет ввести преобразование e = е + w, чтобы
    # 0 <= e <= 1.
    w = 1 - m

    # начало основного цикла
    x = xn
    y = yn
    dots = []
    for i in range(dx + 1):
        cur_color = change_color_intensity(color, e)
        dots.append([x, y, cur_color])
        if e > w:
            if change_flag:
                x += signx
            else:
                y += signy
            e -= 1
        if change_flag:
            y += signy
        else:
            x += signx
        e += m

    return dots


# подобно Брезенхему, но в алгоритме Ву на каждом шаге устанавливается не одна, а две точки.
# алгоритм принимает не целые координаты концов отрезка, а вещественные.
def wu(xn, yn, xk, yk, color):
    dx = xk - xn
    dy = yk - yn

    change_flag = abs(dx) < abs(dy)

    # замена y(x) на x(y) в зависимости от углового коэффициента
    if change_flag:
        xn, xk, yn, yk = yn, yk, xn, xk
        dx, dy = dy, dx

    # построение ведется слева направо (снизу вверх)
    if xn > xk:
        xn, xk = xk, xn
        yn, yk = yk, yn

    # угловой коэффициент
    m = dy / dx

    dots = []

    # обработать начальную точку
    xend = round(xn)
    yend = yn + m * (xend - xn)
    xgap = 1 - (xn + 0.5) % 1
    xpxl1 = xend  # будет использоваться в основном цикле
    ypxl1 = int(yend)
    intensity = 1 - (yend % 1) * xgap
    cur_color = change_color_intensity(color, intensity)
    dots.append([xpxl1, ypxl1, cur_color])
    intensity = (yn % 1) * xgap
    cur_color = change_color_intensity(color, intensity)
    dots.append([xpxl1, ypxl1 + 1, cur_color])

    # первое y-пересечение для цикла
    intery = yend + m

    # обработать конечную точку
    xend = round(xk)
    yend = yk + m * (xend - xk)
    xgap = (xk + 0.5) % 1
    xpxl2 = xend  # будет использоваться в основном цикле
    ypxl2 = int(yend)
    intensity = 1 - (yend % 1) * xgap
    cur_color = change_color_intensity(color, intensity)
    dots.append([xpxl2, ypxl2, cur_color])
    intensity = (yk % 1) * xgap
    cur_color = change_color_intensity(color, intensity)
    dots.append([xpxl2, ypxl2 + 1, cur_color])

    def change_xy(xp, yp, flag):
        if flag:
            return [yp, xp]
        else:
            return [xp, yp]

    # основной цикл
    for x in range(xpxl1 + 1, xpxl2):
        intensity = 1 - intery % 1
        cur_color = change_color_intensity(color, intensity)
        dots.append([*change_xy(x, int(intery), change_flag), cur_color])

        intensity = intery % 1
        cur_color = change_color_intensity(color, intensity)
        dots.append([*change_xy(x, int(intery) + 1, change_flag), cur_color])
        intery += m

    return dots


def lib(xn, yn, xk, yk, color):
    return ['lib', xn, yn, xk, yk, color]

