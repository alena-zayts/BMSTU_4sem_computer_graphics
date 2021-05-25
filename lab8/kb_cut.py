ERR_CONV = -1
ERR_DEG = -2
OK = 0
EPS = 1e-6


# определение "знака" (знака проекции на ось z) векторного произведения
# векторов [point1, point2] и [point2, point3]
def vect_mult_sign_z(point1, point2, point3):
    x1 = point2[0] - point1[0]
    y1 = point2[1] - point1[1]
    x2 = point3[0] - point2[0]
    y2 = point3[1] - point2[1]
    z = x1 * y2 - y1 * x2
    if z > 0:
        return 1
    elif z < 0:
        return -1
    return 0


# скалярное произведение векторов vec1 и vec2
def scalar_mult(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1]


# знак скалярного произведения векторов vec1 и vec2
def scalar_mult_sign(vec1, vec2):
    sm = scalar_mult(vec1, vec2)
    if sm > 0:
        return 1
    elif sm < 0:
        return -1
    return 0


# внутренняя нормаль к стороне [point1, point2] (следующая вершина служит для
# проверки того, какая нормаль найдена: внутренняя или внешняя)
# точки не должны лежать на одной прямой
def inner_normal(point1, point2, point3):
    i = point2[0] - point1[0]
    j = point2[1] - point1[1]

    if j == 0:
        normal = [0, 1]
    else:
        normal = [j, -i]

    if scalar_mult_sign(normal, [point3[0] - point2[0], point3[1] - point2[1]]) < 0:
        normal[0] *= -1
        normal[1] *= -1

    return normal


# часть отрезка [point1, point2] от t_beg до t_end
def new_segment(point1, point2, t_beg, t_end):
    x_beg = point1[0] + (point2[0] - point1[0]) * t_beg
    y_beg = point1[1] + (point2[1] - point1[1]) * t_beg
    x_end = point1[0] + (point2[0] - point1[0]) * t_end
    y_end = point1[1] + (point2[1] - point1[1]) * t_end
    return list(map(round, [x_beg, y_beg, x_end, y_end]))


# найти уравнение прямой вида ax+by+c=0, проходящей через точки dot1 и dot2
def find_line_by_2points(dot1, dot2):
    # из уравнения прямой, проходящей через 2 точки
    # (x - x1)/ (x2 - x1) = (y - y1) / (y2 - y1)
    a = dot2[1] - dot1[1]
    b = dot1[0] - dot2[0]
    c = dot2[0] * dot1[1] - dot1[0] * dot2[1]
    line = {'a': a, 'b': b, 'c': c}
    return line


# найти точку пересечения 2 прямых line1 и line2
def find_lines_intersection(line1, line2):
    # параллельные
    if abs(line1['a'] * line2['b'] - line2['a'] * line1['b']) < EPS:
        return None
    if abs(line1['a']) < EPS and abs(line1['b']) < EPS:
        print('Ошибка в функции find_lines_intersection: \
первое уравнение - не прямая')
        return
    # точка должна принадлежать обеим прямым, поэтому получаем систему
    # a1x + b1y + c1 = 0
    # a2x + b2y + c2 = 0
    # если первая прямая параллельна оси ox
    if abs(line1['a']) < EPS:
        y0 = -1 * line1['c'] / line1['b']
        x0 = ((line2['b'] * line1['c'] - line1['b'] * line2['c']) /
              (line1['b'] * line2['a']))
    else:
        y0 = ((line2['a'] * line1['c'] - line1['a'] * line2['c']) /
              (line1['a'] * line2['b'] - line2['a'] * line1['b']))
        x0 = -1 * (line1['b'] * y0 + line1['c']) / line1['a']
    dot = [x0, y0]
    return dot


# принадлежность точки прямой отрезку
def check_fit(dot, point1, point2):
    if ((min(point1[0], point2[0]) <= dot[0] <= max(point1[0], point2[0])) and
            (min(point1[1], point2[1]) <= dot[1] <= max(point1[1], point2[1]))):
        return True
    return False


# проверка на пересечение сторон прямоугольника
def do_intersect(n, cutter):
    for i in range(n):
        line1 = find_line_by_2points(cutter[i], cutter[i + 1])
        for j in range(n):
            if (j != i) and (j != i - 1) and (j != i + 1) and \
                    not (((i == 0) and (j == n - 1)) or ((j == 0) and (i == n - 1))):
                line2 = find_line_by_2points(cutter[j], cutter[j + 1])
                intersection = find_lines_intersection(line1, line2)
                if (intersection and check_fit(intersection, cutter[i], cutter[i + 1]) and
                        check_fit(intersection, cutter[i], cutter[i + 1])):
                    return True
    return False


# подготовка массива вершин отсекателя
#   отсекатель проверяется на выпуклость
#   если три точки, идущие подряд, лежат на одной прямой, то средняя из них удаляется
#   в конец массива повторно записываются первая и вторая вершины
def prepare_cutter(n, cutter):
    global_direction = 0
    i = 0
    while i < n - 1:
        if i < n - 2:
            cur_direction = vect_mult_sign_z(cutter[i], cutter[i + 1], cutter[i + 2])
        elif i == n - 2:
            cur_direction = vect_mult_sign_z(cutter[i], cutter[i + 1], cutter[0])
        else:
            cur_direction = vect_mult_sign_z(cutter[i], cutter[0], cutter[1])
        if cur_direction == 0:
            if i == n - 1:
                cutter.pop(0)
            else:
                cutter.pop(i + 1)
            n -= 1
        else:
            if global_direction == 0:
                global_direction = cur_direction
            else:
                if global_direction != cur_direction:
                    return ERR_CONV, n, cutter
            i += 1
    if n < 3:
        return ERR_DEG, n, cutter

    cutter.append(cutter[0])
    if do_intersect(n, cutter):
        return ERR_CONV, n, cutter
    cutter.append(cutter[1])
    return OK, n, cutter


def kb_cut(point1, point2, n, C):
    # проверка и подготовка отсекателя
    rc, n, cutter = prepare_cutter(n, C)
    if rc:
        return rc, None
    # начальные значения начала и конца области видимости
    t_beg = 0
    t_end = 1
    # директриса отрезка
    D = [point2[0] - point1[0], point2[1] - point1[1]]

    # цикл отсечения по всем границам
    for i in range(n):
        # вычисляем внутреннюю нормаль к i-й стороне
        normal = inner_normal(C[i], C[i + 1], C[i + 2])
        # вычисляем вектор от начала отрезка до i-й вершины
        W = [point1[0] - C[i][0], point1[1] - C[i][1]]
        # вычисляем два скалярных произведения
        Dsm = scalar_mult(D, normal)
        Wsm = scalar_mult(W, normal)

        # если отрезок параллелен ребру отсекателя или вырожден в точку (P2==P1)
        if Dsm == 0:
            # если расположен по видимую сторону от текущей стороны - отсекать нечего
            if Wsm >= 0:
                continue
            # а если невидим относительно текущей стороны, значит является полностью невидимым
            else:
                return OK, None
        # иначе находим точку пересечения отрезка и текущего ребра
        else:
            t = -Wsm / Dsm

        # если точка пересечения относится к нижней области видимости
        if Dsm > 0:
            # если отрезок пересекает ребро за конечной точкой орезка, то является невидимым
            # относительно текущей стороны, значит является полностью невидимым
            # (так как из нижней области видимости выбираем максимальный параметр t)
            if t > 1:
                return OK, None
            # иначе обновляем нижнюю видимую точку в случае необходимости
            else:
                t_beg = max(t_beg, t)
        # если точка пересечения относится к верхней области видимости - по аналогии
        else:
            if t < 0:
                return OK, None
            else:
                t_end = min(t_end, t)
    # проверка на корректность
    if t_beg <= t_end:
        return OK, new_segment(point1, point2, t_beg, t_end)
    return OK, None
