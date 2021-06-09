from math import pi, sin, cos

M = 80
shx = 1400 / 2 + 50
shy = 1400 / 2 - 50
EPS = 1e-6


def rotateX(x, y, z, teta):
    teta = teta * pi / 180
    buf = y
    y = cos(teta) * y - sin(teta) * z  # +
    z = cos(teta) * z + sin(teta) * buf #-
    return x, y, z


def rotateY(x, y, z, teta):
    teta = teta * pi / 180
    buf = x
    x = cos(teta) * x - sin(teta) * z  # +
    z = cos(teta) * z + sin(teta) * buf  # -
    return x, y, z


def rotateZ(x, y, z, teta):
    teta = teta * pi / 180
    buf = x
    x = cos(teta) * x - sin(teta) * y  # +
    y = cos(teta) * y + sin(teta) * buf # +
    return x, y, z


def tranform(x, y, z, tetax, tetay, tetaz, k):
    x, y, z = rotateX(x, y, z, tetax)
    x, y, z = rotateY(x, y, z, tetay)
    x, y, z = rotateZ(x, y, z, tetaz)
    x *= k
    y *= k
    x = x * M + shx
    y = y * M + shy
    return round(x), round(y), round(z)


def sign(x):
    if not x:
        return 0
    elif x < 0:
        return -1
    return 1


# Отрисовка линии (в зависимости от видимости) и обновление горизонта
# c помощью алгоритма Брезенхема
def brez_horizon(x1, y1, x2, y2, top, bottom, image, color):
    if not(1 <= x1 <= image.width()):
        if not(1 <= x2 <= image.width()):
            return top, bottom
        else:
            x1, y1, x2, y2 = x2, y2, x1, y1

    x = x1
    y = y1
    dx = x2 - x1
    dy = y2 - y1
    sx = sign(dx)
    sy = sign(dy)
    dx = abs(dx)
    dy = abs(dy)

    # если отрезок вырожден
    if dx == 0 and dy == 0 and 1 <= x <= image.width():
        if y > top[x]:
            top[x] = y
            image.setPixel(x, image.height() - y, color)

        if y < bottom[x]:
            bottom[x] = y
            image.setPixel(x, image.height() - y, color)

        return top, bottom

    #  Нужно ли менять местами х и у
    change = 0
    if dy > dx:
        dx, dy = dy, dx
        change = 1
    if 1 <= x <= image.width():
        y_max_curr = top[x]
        y_min_curr = bottom[x]

    e = 2 * dy - dx

    for i in range(dx):
        if not(1 < x < image.width()):
            return top, bottom

        if y > top[x]:
            image.setPixel(x, image.height() - y, color)
            if y > y_max_curr:
                y_max_curr = y

        if y < bottom[x]:
            image.setPixel(x, image.height() - y, color)
            if y < y_min_curr:
                y_min_curr = y

        if e >= 0:
            if change:
                top[x] = y_max_curr
                bottom[x] = y_min_curr
                x += sx
                y_max_curr = top[x]
                y_min_curr = bottom[x]
            else:
                y += sy
            e -= 2 * dx

        if e < 0:
            if not change:
                top[x] = y_max_curr
                bottom[x] = y_min_curr
                x += sx
                y_max_curr = top[x]
                y_min_curr = bottom[x]
            else:
                y += sy
            e += 2 * dy

    return top, bottom


def float_horizon(scene_width, scene_hight,
                  x_min, x_max, x_step,
                  z_min, z_max, z_step,
                  tx, ty, tz, k,
                  func, image, color):
    # для боковых ребер
    x_right, y_right, x_left, y_left = -1, -1, -1, -1

    # инициализация горизонтов
    top = {x: 0 for x in range(1, int(scene_width) + 1)}
    bottom = {x: scene_hight for x in range(1, int(scene_width) + 1)}

    # рассекаем поверхность плоскостями, перпендикулярными oz
    z = z_max
    while z > (z_min - EPS):
        # первая точка на кривой в текущем сечении
        x_prev = x_min
        y_prev = func(x_min, z)
        x_prev, y_prev, z_buf = tranform(x_prev, y_prev, z, tx, ty, tz, k)

        # Обрабатываем левое боковое ребро (соединяем предыдущюю левую с текущей)
        if x_left != -1:
            top, bottom = brez_horizon(x_prev, y_prev, x_left, y_left, top, bottom, image, color)
        x_left = x_prev
        y_left = y_prev

        # в цикле по точками на кривой в текущем сечении
        x = x_min
        while x <= x_max:
            y = func(x, z)
            x_curr, y_curr, z_buf = tranform(x, y, z, tx, ty, tz, k)
            # соединяем предыдущую с текущей
            top, bottom = brez_horizon(x_prev, y_prev, x_curr, y_curr, top, bottom, image, color)

            x_prev = x_curr
            y_prev = y_curr
            x += x_step

        # Обрабатываем правое ребро (соединяем предыдущюю правую с текущей)
        if x_right != -1:
            top, bottom = brez_horizon(x_prev, y_prev, x_right, y_right, top, bottom, image, color)
        x_right = x_prev
        y_right = y_prev

        z -= z_step

    return image
