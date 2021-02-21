from math import sqrt
from tkinter import END, NW, LEFT, LAST, Label, Tk, Entry, Button, Canvas 
import tkinter.messagebox as box

EPS = 10 ** -6
OK = 0
POINTS_MATCH = -1
ONE_LINE = -2
NO_TWO_TANGS = -3

#основной алгоритм
def solve(dots1, dots2):
    # проверка на количество точек в каждом множестве
    # для продолжения решения необходимо, чтобы в каждом множестве была
    # хотя бы одна точка
    if (len(dots1) + len(dots2)) == 0:
        show_dots(dots1, dots2, 'Задача не может быть решена, так как оба \
множества пустые')
        return
    if (len(dots1) == 0):
        show_dots(dots1, dots2, 'Задача не может быть решена, так как первое \
множество пустое')
        return
    if (len(dots2) == 0):
        show_dots(dots1, dots2, 'Задача не может быть решена, так как второе \
множество пустое')
        return
    # поиск всех возможных окружностей, которые могут быть построены на каждом
    # из множеств (совпадающие окружности, построенные на разном наборе точек,
    # считаются различными) (в информацию об окружности включается координаты
    # ее центра, радиус, а также номера точек, на которых она построена),
    #а также комбинаций точек на каждом множестве, на
    # которых невозможно построить окружности.
    all_circles1, empty_circles1 = make_circles_table(dots1)
    all_circles2, empty_circles2 = make_circles_table(dots2)
    ac1 = len(all_circles1)
    ac2 = len(all_circles2)
    # проверка на количество окуружностей, которые можно построить на каждом 
    # множестве
    # для продолжения решения необходимо, чтобы в каждом множестве была
    # хотя бы одна окружность
    if (len(all_circles1) + len(all_circles2)) == 0:
        show_dots(dots1, dots2, 'Задача не может быть решена, так как ни на \
одном из множеств\n нельзя построить окружность')
        return
    if (len(all_circles1) == 0):
        show_dots(dots1, dots2, 'Задача не может быть решена, так как на \
первом множестве\n нельзя построить окружность')
        return
    if (len(all_circles2) == 0):
        show_dots(dots1, dots2, 'Задача не может быть решена, так как на \
втором множестве\n нельзя построить окружность')
        return
    #для сокращения вычислений, оставляем только несовпадающие окружности в
    #каждом множестве
    circles1 = leave_unique_circles(all_circles1)
    circles2 = leave_unique_circles(all_circles2)
    # составляем 1)таблицу из комбинаций окружностей, к которым можно провести две
    # внутренние касательные (в таблицу включается информация о каждой окружности,
    # касательной, а также точки пересечения каждой касательной с каждой 
    # окружностью и точка пересечения касательных между собой) 2)список из 
    # комбинаций окружностей, к которым нельзя провести две внутренние касательные
    tangs_table, empty_tangs = make_tangs_table(circles1, circles2)
    # проверка на количество комбинаций окуружностей, к которым  можно 
    # провести 2 внутренние касательные
    # для продолжения решения необходимо, чтобы была
    # хотя бы одна такая комбинация
    if len(tangs_table) == 0:
        show_dots(dots1, dots2, 'Задача не может быть решена, так ни в одной \
комбинации из\n окружностей первого и второго множеств нельзя \n\
построить две внутренние касательные')
        return
    
    #Добавление в таблицу разниц площадей четырехугольников, образованных 
    #центрами окружностей, точками касания внутренних общих касательных
    #и точкой пересечения касательных
    full_info = find_areas(tangs_table)
    #выбор комбинации с наибольшей разницей искомых площадей
    full_info.sort(key=sort_by_s_dif, reverse=True)
    answer_case = full_info[0]
    
    #дополнительная информация (пояснения) к решению
    add = (len(dots1), len(dots2),
           ac1 + len(empty_circles1), 
           ac2 + len(empty_circles2),
           ac1, ac2, 
           len(circles1), len(circles2),
           len(empty_circles1), len(empty_circles2),
           len(circles1) * len(circles2),
           len(full_info),
           len(empty_tangs))
    text_added = 'Дополнительная информация:\n\
    всего точек: 1)%d  2)%d\n\
    всего возможных комбинаций точек: 1)%d  2)%d\n\
    всего возможных окружностей:      1)%d  2)%d\n\
    уникальных окружностей:           1)%d  2)%d\n\
    комбинаций, на которых нельзя построить окружность: 1)%d 2)%d\n\n\
    всего возможных комбинаций окружностей: %d\n\
    можно провести 2 внутренние касательные в %d комбинациях\n\
    нельзя в %d кобинациях'%(add)
    
    #визуализация решения
    show_answer(answer_case, dots1, dots2, text_added)


# поиск всех возможных окружностей, которые могут быть построены на каждом
# из множеств (совпадающие окружности, построенные на разном наборе точек,
# считаются различными) (в информацию об окружности включается координаты
# ее центра, радиус, а также номера точек, на которых она построена),
#а также комбинаций точек на каждом множестве, на
# которых невозможно построить окружности.
# возвращает таблицу всех возможных окружностей и список всех кобинаций точек, 
# на которых нельзя построить окружность
def make_circles_table(dots):
    circles_by = [] #таблица всех возможных окружностей
    empty_circles = [] #список всех кобинаций точек, на которых 
                       #нельзя построить окружность
    #полный перебор всех возможных комбинаций
    for i in range(len(dots) - 2):
        for j in range(i + 1, len(dots) - 1):
            for k in range(j + 1, len(dots)):
                #возможно ли построить окружность на точках i, j, k
                if circle_exists(dots[i], dots[j], dots[k]) == OK:
                # если да, то находим эту окружность (координаты центра и радиус)
                # и добавляем ее в таблицу, указывая номера точек, на которых
                # она построена
                    circle = find_circle(dots[i], dots[j], dots[k])
                    circle['by'] = [i ,j, k]
                    circles_by.append(circle)
                else:
                    #иначе - добавляем эту кобинацию в соответствующий список
                    empty_circles.append([i, j, k])
    return circles_by, empty_circles

#возможно ли построить окружность на точках dot1, dot2, dot3
def circle_exists(dot1, dot2, dot3):
    #нет, если хотя бы две из них совпадают
    if (((abs(dot1['x'] - dot2['x']) < EPS) and
         (abs(dot1['y'] - dot2['y']) < EPS)) or
        ((abs(dot1['x'] - dot3['x']) < EPS) and
         (abs(dot1['y'] - dot3['y']) < EPS)) or 
        ((abs(dot3['x'] - dot2['x']) < EPS) and
         (abs(dot3['y'] - dot2['y']) < EPS))):
        return POINTS_MATCH

    #нет, если все точки лежат на одной прямой, ...
    if ((abs(dot1['x'] - dot2['x']) < EPS and
         abs(dot1['x'] - dot3['x']) < EPS) or # ..параллельной oy
        (abs(dot1['y'] - dot2['y']) < EPS and
         abs(dot1['y'] - dot3['y']) < EPS)): # ..параллельной ox
        return ONE_LINE
    # избегаем деления на нуль в следующей операции, меняя последовательность
    # точек так, чтобы точки 2 и 3 не совпадали по x или y
    while ((abs(dot3['y'] - dot2['y']) < EPS) or 
           (abs(dot3['x'] - dot2['x']) < EPS)):
        dot1, dot2, dot3 = dot2, dot3, dot1
    # ...не параллельной ни ox, ни oy 
    # из уравнения прямой, проходящей через 2 точки
    # (x - x1)/ (x2 - x1) = (y - y1) / (y2 - y1)
    if (abs((dot1['y'] - dot2['y'])/(dot3['y'] - dot2['y']) - 
            (dot1['x'] - dot2['x'])/(dot3['x'] - dot2['x'])) < EPS):
        return ONE_LINE
    #во всех других случаях - возможно
    return OK

#найти центр и радиус окружности, проходящей через точки dot1, dot2, dot3
# (см вывод)
def find_circle(dot1, dot2, dot3):
    # прямые, проходящие через точки (dot1 и dot2) и (dot2 и dot3)
    line_1 = find_line_by_2points(dot1, dot2)
    line_2 = find_line_by_2points(dot2, dot3)
    # середины отрезков (dot1, dot2) и (dot2, dot3)
    mid_1 = find_middle(dot1, dot2)
    mid_2 = find_middle(dot2, dot3)
    # серединые перпендикуляры отрезков (dot1, dot2) и (dot2, dot3)
    perp_1 = find_perp(mid_1, line_1)
    perp_2 = find_perp(mid_2, line_2)
    # точка пересечения серединных перпендикуляров - центр искомой окружности
    centre = find_lines_intersection(perp_1, perp_2)
    #радиус - расстояние от центра до любой точки на окружности
    r = distance(dot1, centre)
    circle = {'centre' : centre, 'r' : r}
    return circle

#найти уравнение прямой вида ax+by+c=0, проходящей через точки dot1 и dot2
# (cм вывод)                   
def find_line_by_2points(dot1, dot2):
    # из уравнения прямой, проходящей через 2 точки
    # (x - x1)/ (x2 - x1) = (y - y1) / (y2 - y1)
    a = dot2['y'] - dot1['y']
    b = dot1['x'] - dot2['x']
    c = dot2['x'] * dot1['y'] - dot1['x'] * dot2['y']
    line = {'a' : a, 'b' : b, 'c' : c}
    return line

#найти точку - середину отрезка (dot1, dot2)
def find_middle(dot1, dot2):
    xm = (dot2['x'] + dot1['x']) / 2
    ym = (dot2['y'] + dot1['y']) / 2
    dotm = {'x' : xm, 'y' : ym}
    return dotm

#найти перпендикуляр из точки dot к прямой line
def find_perp(dot, line):
    #находим коэффициент наклона семейства прямых, перпендикулярных line
    # k1 * k2 = -1
    an = -line['b']
    bn = line['a']
    # из семейства прямых, перпендикулярных line, выбираем ту, которая проходит
    #проходит через точку dot из уравнения прямой
    # an * x + bn * y + cn = 0
    cn = -(an * dot['x'] + bn * dot['y'])
    perp = {'a' : an, 'b' : bn, 'c' : cn}
    return perp

#найти точку пересечения 2 прямых line1 и line2
# (см вывод)
def find_lines_intersection(line1, line2):
    #в функцию не должны подаваться параллельные прямые или неверные данные
    #лишняя проверка, чтобы не допустить деления на нуль
    if (abs(line1['a'] * line2['b'] - line2['a'] * line1['b']) < EPS):
        print('Ошибка в функции find_lines_intersection: \
переданы параллельные прямые')
        return       
    if (abs(line1['a']) < EPS and abs(line1['b']) < EPS):
        print('Ошибка в функции find_lines_intersection: \
первое уравнение - не прямая')
        return
    #точка должна принадлежать обеим прямым, поэтому получаем систему
    #a1x + b1y + c1 = 0
    #a2x + b2y + c2 = 0
    #см вывод формул
    #если первая прямая параллельна оси ox
    if (abs(line1['a']) < EPS):
        y0 = -1 * line1['c'] / line1['b']
        x0 = ((line2['b'] * line1['c'] - line1['b'] * line2['c']) / 
              (line1['b'] * line2['a']))
    else:
        y0 = ((line2['a'] * line1['c'] - line1['a'] * line2['c']) / 
              (line1['a'] * line2['b'] - line2['a'] * line1['b']))
        x0 = -1 * (line1['b'] * y0 + line1['c']) / line1['a']
    dot = {'x' : x0, 'y' : y0}
    return dot

#расстояние между 2 точками dot1, dot2
def distance(dot1, dot2):
    return sqrt((dot1['x'] - dot2['x']) ** 2 + (dot1['y'] - dot2['y']) ** 2)

#оставить только несовпадающие окружности из множества окружностей
def leave_unique_circles(circles):
    to_pop = set() #индексы окружностей, которые нужно удалить
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            if ((abs(circles[i]['centre']['x'] - 
                     circles[j]['centre']['x']) < EPS) and
                (abs(circles[i]['centre']['y'] - 
                     circles[j]['centre']['y']) < EPS) and
                (abs(circles[i]['r'] - circles[j]['r']) < EPS)):
                to_pop.add(j)
    to_pop = sorted(to_pop, reverse=True)
    #удаление окружностей
    for i in to_pop:
        circles.pop(i)
    return circles

# составить 1)таблицу из комбинаций окружностей, к которым можно провести две
# внутренние касательные (в таблицу включается информация о каждой окружности,
# касательной, а также точки пересечения каждой касательной с каждой 
# окружностью и точка пересечения касательных между собой) 2)список из
# комбинаций окружностей, к которым нельзя провести две внутренние касательные
def make_tangs_table(circles1, circles2):
    empty_tangs = [] #таблица неподходящих комбинаций
    tangs_table = [] #таблица подходящих комбинаций
    for circle1 in circles1:
        for circle2 in circles2:
            #если к комбинации окружностей можно провести две
            # внутренние касательные
            if tangs_exist(circle1, circle2) == OK:
                # находим все касательные (2 внутренние и 2 внешние)
                all_tangs = find_tangs(circle1, circle2)
                #из всех касательных выбираем 2 внутренние
                inner_tangs = choose_inner_tangs(all_tangs, 
                                                 circle1['centre'],
                                                 circle2['centre'])
                #находим точки, в которых касательные касаются окружностей
                c1t1 = find_touch_point(circle1, inner_tangs[0])
                c1t2 = find_touch_point(circle1, inner_tangs[1])
                c2t1 = find_touch_point(circle2, inner_tangs[0])
                c2t2 = find_touch_point(circle2, inner_tangs[1])
                t1t2 = find_lines_intersection(inner_tangs[0], 
                                               inner_tangs[1])
                #формируем и добавляем информацию о комбинации
                info = {'c1' : circle1, 'c2' : circle2, 'c1t1' : c1t1,
                        'c1t2' : c1t2,'c2t1' : c2t1, 'c2t2' : c2t2, 
                        't1t2' : t1t2, 't1' : inner_tangs[0],
                        't2' : inner_tangs[1]}
                tangs_table.append(info)
            #иначе добавляем комбинацию в таблицу неподходящих комбинаций
            else:
                empty_tangs.append([circle1, circle2])
    return  tangs_table, empty_tangs

#можно ли провести 2 внутренние касательные к окружностям
def tangs_exist(circle1, circle2):
    #можно только если каждая из окружностей лежит вне другой и
    # они не пересекаются)
    if (distance(circle1['centre'], circle2['centre']) - 
        (circle1['r'] + circle2['r'])) < EPS:
        return NO_TWO_TANGS
    return OK  

#найти все касательные (2 внутренние и 2 внешние) к окружностям
# (см вывод)
def find_tangs(circle1, circle2):
    x1 = circle1['centre']['x']
    x2 = circle2['centre']['x']
    y1 = circle1['centre']['y']
    y2 = circle2['centre']['y']
    r1 = circle1['r']
    r2 = circle2['r']
    #перемещаем окружности так, чтобы центр первой находился в начале координат
    x2 -= x1
    y2 -= y1
    
    #перебираем все возможные расположения касательных относительно окружностей
    d1 = r1
    d2 = r2
    a1 = (((d2 - d1) * x2 + y2 * sqrt(x2 ** 2 + y2 ** 2 - (d2 - d1) ** 2))
          / (x2 **2 + y2 **2))
    b1 = (((d2 - d1) * y2 - x2 * sqrt(x2 ** 2 + y2 ** 2 - (d2 - d1) ** 2))
          / (x2 **2 + y2 **2))
    #за счет вычитания, сдвигаем картину обратно
    c1 = d1 - (a1 * x1 + b1 * y1)
    
    d1 = -r1
    d2 = r2
    a2 = (((d2 - d1) * x2 + y2 * sqrt(x2 ** 2 + y2 ** 2 - (d2 - d1) ** 2))
          / (x2 **2 + y2 **2))
    b2 = (((d2 - d1) * y2 - x2 * sqrt(x2 ** 2 + y2 ** 2 - (d2 - d1) ** 2))
          / (x2 **2 + y2 **2))
    c2 = d1 - (a2 * x1 + b2 * y1)
    
    d1 = r1
    d2 = -r2
    a3 = (((d2 - d1) * x2 + y2 * sqrt(x2 ** 2 + y2 ** 2 - (d2 - d1) ** 2))
          / (x2 **2 + y2 **2))
    b3 = (((d2 - d1) * y2 - x2 * sqrt(x2 ** 2 + y2 ** 2 - (d2 - d1) ** 2))
          / (x2 **2 + y2 **2))
    c3 = d1 - (a3 * x1 + b3 * y1)
    
    d1 = -r1
    d2 = -r2
    a4 = (((d2 - d1) * x2 + y2 * sqrt(x2 ** 2 + y2 ** 2 - (d2 - d1) ** 2))
          / (x2 **2 + y2 **2))
    b4 = (((d2 - d1) * y2 - x2 * sqrt(x2 ** 2 + y2 ** 2 - (d2 - d1) ** 2))
          / (x2 **2 + y2 **2))
    c4 = d1 - (a4 * x1 + b4 * y1)
    
    #формируем ответ
    line1 = {'a' : a1, 'b' : b1, 'c' : c1}
    line2 = {'a' : a2, 'b' : b2, 'c' : c2} 
    line3 = {'a' : a3, 'b' : b3, 'c' : c3}
    line4 = {'a' : a4, 'b' : b4, 'c' : c4}
    all_tangs = [line1, line2, line3, line4]
    return all_tangs

#выбрать из всех касательных 2 внутренние
def choose_inner_tangs(tangs, centre1, centre2):
    for i in range(len(tangs) - 1):
        for j in range(i + 1, len(tangs)):
            #внутренние касательные не могут быть параллельны
            if ((abs(tangs[i]['a'] * tangs[j]['b'] - 
                     tangs[i]['b'] * tangs[j]['a']) > EPS)
                or (abs(tangs[i]['a'] * tangs[j]['a'] + 
                        tangs[i]['b'] * tangs[j]['b']) < EPS)):
                #находим, где пересекаются выбранные касательные
                inters = find_lines_intersection(tangs[i], tangs[j])
                #если обе касательные - внутренние, то точка их пересечения
                #находится в прямоугольнике, противоположные вершины которого -
                #центры окружностей
                if ((min(centre1['x'], centre2['x']) <= inters['x'] <=
                    max(centre1['x'], centre2['x'])) and
                    (min(centre1['y'], centre2['y']) <= inters['y'] <=
                    max(centre1['y'], centre2['y']))):
                        return [tangs[i], tangs[j]]
                    
# найти точку касания касательной и окружности                   
def find_touch_point(circle, tan):
    #находим перпендикуляр из центра к касательной
    perp = find_perp(circle['centre'], tan)
    #находим точку пересечения перпендикуляра и касательной
    dot = find_lines_intersection(tan, perp)
    return dot

#найти разность площадей четырехугольников для всех комбинаций подходящих 
#окружностей
def find_areas(info_table):
    for case in info_table:
        s1 = find_area(case['c1t1'], case['c1']['centre'], case['c1t2'],
                       case['t1t2'])
        s2 = find_area(case['c2t1'], case['c2']['centre'], case['c2t2'], 
                       case['t1t2'])
        case['s1'] = s1
        case['s2'] = s2
        case['s_dif'] = abs(s1 - s2)
    return info_table

#найти площадь четырехугольника по 4 вершинам
# (см вывод)
def find_area(dot1, dot2, dot3, dot4):
    # S = d1*d2*sin(p)/2
    #длины диагоналей
    d1 = distance(dot1, dot3)
    d2 = distance(dot2, dot4)
    #уравнения диагоналей
    line1 = find_line_by_2points(dot1, dot3)
    line2 = find_line_by_2points(dot2, dot4)
    #косинус и синус угла между диагоналями
    cos_angle = find_cos(line1, line2)
    sin_angle = sqrt(1 - cos_angle * cos_angle)
    
    s = d1 * d2 * sin_angle / 2
    return s

#найти косинус угла между прямыми 
#рассматриваем уравнения прямых как векторы v1 = (a1, b1), v2 = (a2, b2)
# (см вывод)
def find_cos(line1, line2):
    #cos(p) = (v1, v2)/(|v1| * |v2|)
    mul = line1['a'] * line2['a'] + line1['b'] * line2['b']
    mod1 = sqrt(line1['a'] * line1['a'] + line1['b'] * line1['b'])
    mod2 = sqrt(line2['a'] * line2['a'] + line2['b'] * line2['b'])
    cos_angle = mul / (mod1 * mod2)
    return cos_angle

#для сортировки комбинаций по разности площадей
def sort_by_s_dif(case):
        return case['s_dif']

# визуализация решения в случае отсутсвия ответа - выводятся только точки
def show_dots(dots1, dots2, message):
    #создание окна для ответа
    SIZE = 600
    border = 80
    color1 = 'red'
    color2 = 'green'
    borders = 2
    root = Tk()
    root.title('Визуализация (только точки)')
    root.geometry('%dx600+30+30'%(SIZE + 600))
    root.resizable(width=False, height=False)
    canv = Canvas(root, width = SIZE, height = SIZE, bg = "white")
    
    #масштабирование
    all_dots = []
    for dot in dots1:
        all_dots.append(dot)
    for dot in dots2:
        all_dots.append(dot)
    unique_dots = leave_unique_dots(all_dots)
    x = []
    y = []
    for dot in unique_dots:
        x.append(dot['x'])
        y.append(dot['y'])
    if (len(x) > 1):  
        x_max = max(x)
        x_min = min(x)
        y_max = max(y)
        y_min = min(y)
    elif (len(x) == 1):
        x_max = abs(x[0]) * 2
        x_min = -abs(x[0]) * 2
        y_max = abs(y[0]) * 2
        y_min = -abs(y[0]) * 2
    else:
        x_max = 1
        x_min = -1
        y_max = 1
        y_min = -1
    zn = max(abs(x_max - x_min),abs(y_max - y_min))
    if (zn):
        s = (SIZE - border*2)/zn
    else:
        s = (SIZE - border*2) 
         
    #прорисовка осей
    #oy
    x1 = (0 - x_min) * s + border
    y1 = SIZE
    x2 = (0 - x_min) * s + border
    y2 = 0
    canv.create_line(x1, y1, x2, y2, width=2,arrow=LAST)
    canv.create_text(x2+10, y2+10, text='Y')                                                      
    #ox
    x1 = 0
    y1 = SIZE - ((0 - y_min) * s + border)
    x2 = SIZE
    y2 = SIZE - ((0 - y_min) * s + border)
    canv.create_line(x1, y1, x2, y2, width=2,arrow=LAST) 
    canv.create_text(x2-10, y2-10, text='X')           
     
    #прорисовка точек первого множества
    for i in range(len(dots1)):
        dot = dots1[i]
        x0 = (dot['x'] - x_min) * s + border
        y0 = SIZE - ((dot['y'] - y_min) * s + border)
        
        canv.create_oval(x0-borders,y0-borders,x0+borders,y0+borders,
                         fill=color1)
        canv.create_text(x0-5,y0-5,text= '%d (%.2f, %.2f)'%(
            (i+1), dot['x'], dot['y']))
    
    #прорисовка точек второго множества
    for i in range(len(dots2)):
        dot = dots2[i]
        x0 = (dot['x'] - x_min) * s + border
        y0 = SIZE - ((dot['y'] - y_min) * s + border)
    
        canv.create_oval(x0-borders,y0-borders,x0+borders,y0+borders,
                         fill=color2)
        canv.create_text(x0-5,y0-5,text= '%d (%.2f, %.2f)'%(
            (i+1), dot['x'], dot['y']))
    # размещение текста с описанием цветов
    canv.place(x = 0, y = 0)
    text_red = 'красный - точки первого множества'
    lbl_red = Label(root,text = text_red, fg='red',
                          font='arial 11', justify = LEFT, bg = 'mint cream')
    lbl_red.place(x = SIZE, y = 0, width = 600, height = 20, anchor= NW)
    
    text_green = 'зеленый - точки второго множества'
    lbl_green = Label(root,text = text_green, fg='green', 
                          font='arial 11', justify = LEFT, bg = 'mint cream')
    lbl_green.place(x = SIZE, y = 20, width = 600, height = 20, anchor= NW)
    
    # размещение текста с причиной отсутствия ответа
    lbl_message = Label(root,text = message,
                          font='arial 11', justify = LEFT, bg = 'mint cream')
    lbl_message.place(x = SIZE, y = 40, width = 600, height = 400, anchor= NW)
    
    #запуск цикла обработки событий
    root.mainloop()
    
# визуализация решения в случае успешного решения  
def show_answer(answer_case, dots1, dots2, text_added):
    #создание окна
    SIZE = 600
    border = 80
    color1 = 'red'
    color2 = 'green'
    colort = 'blue'
    colord = 'black'
    colorr = 'black'
    borders = 2
    root = Tk()
    root.title('Визуализация решения')
    root.geometry('%dx600+30+30'%(SIZE + 600))
    root.resizable(width=False, height=False)
    canv = Canvas(root, width = SIZE, height = SIZE, bg = "white")    
    
    #масштабирование
    circle1 = answer_case['c1']
    circle2 = answer_case['c2']
    x_max = max(circle1['centre']['x'] + circle1['r'],
                circle2['centre']['x'] + circle2['r'])
    x_min = min(circle1['centre']['x'] - circle1['r'],
                circle2['centre']['x'] - circle2['r'])
    y_max = max(circle1['centre']['y'] + circle1['r'],
                circle2['centre']['y'] + circle2['r'])
    y_min = min(circle1['centre']['y'] - circle1['r'],
                circle2['centre']['y'] - circle2['r'])
    zn = max(abs(x_max - x_min),abs(y_max - y_min))
    s = (SIZE - border*2)/zn
    
    #прорисовка 
    #оси
    #oy
    x1 = (0 - x_min) * s + border
    y1 = SIZE
    x2 = (0 - x_min) * s + border
    y2 = 0
    canv.create_line(x1, y1, x2, y2, width=2,arrow=LAST)
    canv.create_text(x2+10, y2+10, text='Y')                                                      
    #ox
    x1 = 0
    y1 = SIZE - ((0 - y_min) * s + border)
    x2 = SIZE
    y2 = SIZE - ((0 - y_min) * s + border)
    canv.create_line(x1, y1, x2, y2, width=2,arrow=LAST) 
    canv.create_text(x2-10, y2-10, text='X')                 
     
    #окружность, построенная на точках первого множества
    x1 = (circle1['centre']['x'] - circle1['r'] - x_min)*s + border
    y1 = SIZE - ((circle1['centre']['y'] - circle1['r'] - y_min)*s + border)
    x2 = (circle1['centre']['x'] + circle1['r'] - x_min)*s + border
    y2 = SIZE - ((circle1['centre']['y'] + circle1['r'] - y_min)*s + border)
    x0 = (circle1['centre']['x'] - x_min)*s + border
    y0 = SIZE - ((circle1['centre']['y'] - y_min)*s + border)
    
    canv.create_oval(x0-borders,y0-borders,x0+borders,y0+borders,fill=colord)
    canv.create_text(x0-5,y0-5,text= 'c1 (%.2f, %.2f)'%(circle1['centre']['x'], 
                                                       circle1['centre']['y']))
    canv.create_oval(x1, y1, x2, y2, outline = color1, width = borders)
    
    #окружность, построенная на точках второго множества
    x1 = (circle2['centre']['x'] - circle2['r'] - x_min)*s + border
    y1 = SIZE - ((circle2['centre']['y'] - circle2['r'] - y_min)*s + border)
    x2 = (circle2['centre']['x'] + circle2['r'] - x_min)*s + border
    y2 = SIZE - ((circle2['centre']['y'] + circle2['r'] - y_min)*s + border)
    x0 = (circle2['centre']['x'] - x_min)*s + border
    y0 = SIZE - ((circle2['centre']['y'] - y_min)*s + border)
    
    canv.create_oval(x0-borders,y0-borders,x0+borders,y0+borders,fill=colord)
    canv.create_text(x0-5,y0-5,text= 'c2 (%.2f, %.2f)'%(circle2['centre']['x'], 
                                                       circle2['centre']['y']))
    canv.create_oval(x1, y1, x2, y2, outline = color2, width = borders)
    
    #касательные
    x1 = (answer_case['c1t1']['x'] - x_min) * s + border
    y1 = SIZE - ((answer_case['c1t1']['y'] - y_min) * s + border)
    x2 = (answer_case['c2t1']['x'] - x_min) * s + border
    y2 = SIZE - ((answer_case['c2t1']['y'] - y_min) * s + border)
    canv.create_line(x1, y1, x2, y2, width=2,fill=colort)
    
    x1 = (answer_case['c1t2']['x'] - x_min) * s + border
    y1 = SIZE - ((answer_case['c1t2']['y'] - y_min) * s + border)
    x2 = (answer_case['c2t2']['x'] - x_min) * s + border
    y2 = SIZE - ((answer_case['c2t2']['y'] - y_min) * s + border)
    canv.create_line(x1, y1, x2, y2, width=2,fill=colort)
    
    #пересечение касательных
    x0 = (answer_case['t1t2']['x'] - x_min)*s + border
    y0 = SIZE - ((answer_case['t1t2']['y'] - y_min)*s + border)
    canv.create_oval(x0-borders,y0-borders,x0+borders,y0+borders,fill=colord)
    canv.create_text(x0-5,y0-5,
                     text= 'K (%.2f, %.2f)'%(answer_case['t1t2']['x'], 
                                                    answer_case['t1t2']['y']))
    
    #радиусы к касательным
    #первая окружноссть - первая касательная
    x1 = (answer_case['c1t1']['x'] - x_min) * s + border
    y1 = SIZE - ((answer_case['c1t1']['y'] - y_min) * s + border)
    x2 = (circle1['centre']['x'] - x_min) * s + border
    y2 = SIZE - ((circle1['centre']['y'] - y_min) * s + border)
    canv.create_line(x1, y1, x2, y2, width=2,fill=colorr)
    #первая окружноссть - вторая касательная
    x1 = (answer_case['c1t2']['x'] - x_min) * s + border
    y1 = SIZE - ((answer_case['c1t2']['y'] - y_min) * s + border)
    x2 = (circle1['centre']['x'] - x_min) * s + border
    y2 = SIZE - ((circle1['centre']['y'] - y_min) * s + border)
    canv.create_line(x1, y1, x2, y2, width=2,fill=colorr)
    #вторая окружноссть - первая касательная
    x1 = (answer_case['c2t1']['x'] - x_min) * s + border
    y1 = SIZE - ((answer_case['c2t1']['y'] - y_min) * s + border)
    x2 = (circle2['centre']['x'] - x_min) * s + border
    y2 = SIZE - ((circle2['centre']['y'] - y_min) * s + border)
    canv.create_line(x1, y1, x2, y2, width=2,fill=colorr)
    #вторая окружноссть - вторая касательная
    x1 = (answer_case['c2t2']['x'] - x_min) * s + border
    y1 = SIZE - ((answer_case['c2t2']['y'] - y_min) * s + border)
    x2 = (circle2['centre']['x'] - x_min) * s + border
    y2 = SIZE - ((circle2['centre']['y'] - y_min) * s + border)
    canv.create_line(x1, y1, x2, y2, width=2,fill=colorr)
    
    #точки первого множества
    borders = 3
    for dot_i in circle1['by']:
        dot = dots1[dot_i]
        x0 = (dot['x'] - x_min)*s + border
        y0 = SIZE - ((dot['y'] - y_min)*s + border)
        canv.create_oval(x0-borders,y0-borders,x0+borders,y0+borders,
                         fill=color1)
        canv.create_text(x0-5,y0-5,
                         text= '%d (%.2f, %.2f)'%(dot_i + 1,
                                                  dot['x'], dot['y']))
        
    #точки второго множества
    for dot_i in circle2['by']:
        dot = dots2[dot_i]
        x0 = (dot['x'] - x_min)*s + border
        y0 = SIZE - ((dot['y'] - y_min)*s + border)
        canv.create_oval(x0-borders,y0-borders,x0+borders,y0+borders,
                         fill=color2)
        canv.create_text(x0-5,y0-5,text= '%d (%.2f, %.2f)'%(dot_i + 1, 
                                                            dot['x'], 
                                                       dot['y']))
    #размещение холста
    canv.place(x = 0, y = 0)
    
    # размещение текста с описанием цветов
    text_red = 'красный - точки первого множества и \
окружность, построенная на них'
    lbl_red = Label(root,text = text_red, fg='red',
                          font='arial 11', justify = LEFT, bg = 'mint cream')
    lbl_red.place(x = SIZE, y = 0, width = 600, height = 25, anchor= NW)
    
    text_green = 'зеленый - точки второго множества и \
окружность, построенная на них'
    lbl_green = Label(root,text = text_green, fg='green', 
                          font='arial 11', justify = LEFT, bg = 'mint cream')
    lbl_green.place(x = SIZE, y = 25, width = 600, height = 25, anchor= NW)
    
    text_blue = 'синий - внутренние касательные \
к построенным окружностям'
    lbl_blue = Label(root,text = text_blue, fg='blue', 
                          font='arial 11', justify = LEFT, bg = 'mint cream')
    lbl_blue.place(x = SIZE, y = 50, width = 600, height = 25, anchor= NW)
    
    text_black = 'черный - радиусы, проведенные \
к точкам касания'
    lbl_black = Label(root,text = text_black, fg='black', 
                          font='arial 11', justify = LEFT, bg = 'mint cream')
    lbl_black.place(x = SIZE, y = 75, width = 600, height = 25, anchor= NW)
    
    # размещение текста с ответом
    text_answer = 'Пара окружностей таких, что разность площадей \
четырехугольников,\n\
образованных центрами окружностей, точками касания внутренних общих\n\
кассательных и точкой пересечения касательных, максимальна, может\n\
быть построена на точках:\n\n\
     %d (%.2f, %.2f), %d (%.2f, %.2f), %d (%.2f, %.2f) первого множества и\n\
     %d (%.2f, %.2f), %d (%.2f, %.2f), %d (%.2f, %.2f) второго множества.\n\n\
        площадь оного четырехугольника: %.2f\n\
        площадь другого четырехугольника: %.2f\n\
        разность площадей: %.2f'%(
        circle1['by'][0] + 1, dots1[circle1['by'][0]]['x'], 
        dots1[circle1['by'][0]]['y'],
        circle1['by'][1] + 1, dots1[circle1['by'][1]]['x'], 
        dots1[circle1['by'][1]]['y'],
        circle1['by'][2] + 1, dots1[circle1['by'][2]]['x'], 
        dots1[circle1['by'][2]]['y'],
        circle2['by'][0] + 1, dots2[circle2['by'][0]]['x'], 
        dots2[circle2['by'][0]]['y'],
        circle2['by'][1] + 1, dots2[circle2['by'][1]]['x'], 
        dots2[circle2['by'][1]]['y'],
        circle2['by'][2] + 1, dots2[circle2['by'][2]]['x'], 
        dots2[circle2['by'][2]]['y'],
        answer_case['s1'], answer_case['s2'], answer_case['s_dif'])
    lbl_answer = Label(root,text = text_answer, fg='black', 
                          font='arial 12', justify = LEFT, bg = 'mint cream')
    lbl_answer.place(x = SIZE, y = 110, width = 600, height = 250, anchor= NW)
    
    # размещение текста с дополнительным описанием хода решения
    
    lbl_added = Label(root,text = text_added, fg='black', 
                          font='arial 11', justify = LEFT, bg = 'mint cream')
    lbl_added.place(x = SIZE, y = 370, width = 600, height = 200, anchor= NW)
    
    root.mainloop()


#оставить только уникальные точки множества
def leave_unique_dots(dots):
    to_pop = set()
    for i in range(len(dots)):
        for j in range(i + 1, len(dots)):
            if ((abs(dots[i]['x'] - dots[j]['x']) < EPS) and
                (abs(dots[i]['y'] - dots[j]['y']) < EPS)):
                to_pop.add(j)
    to_pop = sorted(to_pop, reverse=True)
    for i in to_pop:
        dots.pop(i)
    return dots


######################################## операции над интерфейсом
entrys_x1 = []
entrys_y1 = []
entrys_x2 = []
entrys_y2 = []

n1 = 0
n2 = 0
dots1 = []
dots2 = []

#операции с первым множеством
def input_n1():
    global n1
    n1 = entry_n1.get()
    try:
        n1 = int(n1)
    except:
        box.showerror('Ошибка',
        "Количесвто точек должно быть целым неотрицательным числом")
        return
    if n1 < 0:
        box.showerror('Ошибка',
        "Количесвто точек должно быть целым неотрицательным числом")
        return
    entry_n1.configure(state = 'disable')
    but_n1.configure(state = 'disable')
    if (n1 > 10):
        box.showinfo('Внимание',
        "Введите первые 10 точек первого множества через таблицу, а чтобы \
ввести остальные точки, воспользуйтесь опцией 'Добавить'.")
        n1 = 10
        rewrite_n1()
    able_table1(n1)

def able_table1(n):
    for i in range(n):
        entry = entrys_x1[i]
        entry.configure(state = 'normal')
    for i in range(n):
        entry = entrys_y1[i]
        entry.configure(state = 'normal')
    if (n > 0):
        but_dots1.configure(state = 'normal')
    else:
        able_dop1()
        
def input_dots1():
    global n1
    
    x = []
    for i in range(n1):
        x0 = entrys_x1[i].get()
        try:
            x0 = float(x0)
        except:
            box.showerror('Ошибка',
            "Не удалось счиать координату x %d-й точки первого множества."%(
                i + 1) + 
            ' Ожидалось вещественное число. Повторите ввод первой таблицы.')
            return
        else:
            x.append(x0)
    y = []
    for i in range(n1):
        y0 = entrys_y1[i].get()
        try:
            y0 = float(y0)
        except:
            box.showerror('Ошибка',
            "Не удалось счиать координату y %d-й точки первого множества."%(
                i + 1) + 
            ' Ожидалось вещественное число. Повторите ввод первой таблицы.')
            return
        else:
            y.append(y0)     
        
    global dots1
    dots1 = []
    for i in range(n1):
        dot = {'x' : x[i], 'y' : y[i]}
        dots1.append(dot)
        
    rewrite_table1()
    able_dop1()


def able_dop1():
    entry_addx1.configure(state = 'normal')
    entry_addy1.configure(state = 'normal')
    entry_deli1.configure(state = 'normal')
    entry_chi1.configure(state = 'normal')
    entry_chx1.configure(state = 'normal')
    entry_chy1.configure(state = 'normal')
    but_add1.configure(state = 'normal')
    but_del1.configure(state = 'normal')
    but_ch1.configure(state = 'normal')

  
def disable_table1():
    for entry in entrys_x1:
        entry.configure(state = 'disable')
    for entry in entrys_y1:
        entry.configure(state = 'disable')
    but_dots1.configure(state = 'disable')
    
def rewrite_table1():
    able_table1(10)
    clean_table1()
    fill_table1()
    disable_table1()
    
def clean_table1():
    for entry in entrys_x1:
        entry.delete(0, END)
    for entry in entrys_y1:
        entry.delete(0, END)
  
def fill_table1():
    global n1
    global dots1
    for i in range(min(n1, 10)):
        dot = dots1[i]
        entrys_x1[i].insert('insert', '%.2f'%dot['x'])
        entrys_y1[i].insert('insert', '%.2f'%dot['y'])
        
def add1():
    global n1
    global dots1
    x0 = entry_addx1.get()
    try:
        x0 = float(x0)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать координату x добавляемой точки первого множества." + 
        ' Ожидалось вещественное число. Повторите ввод.')
        return 
    y0 = entry_addy1.get()
    try:
        y0 = float(y0)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать координату y добавляемой точки первого множества." + 
        ' Ожидалось вещественное число. Повторите ввод.')
        return 
    n1 += 1
    dot = {'x' : x0, 'y' : y0}
    dots1.append(dot)
    rewrite_table1()
    rewrite_n1()
    entry_addx1.delete(0, END)
    entry_addy1.delete(0, END)

def rewrite_n1():
    global n1
    entry_n1.configure(state = 'normal')
    entry_n1.delete(0, END)
    entry_n1.insert('insert', '%d'%n1)
    entry_n1.configure(state = 'disable')
       
def del1():
    global n1
    global dots1
    
    if (n1 <= 0):
        box.showerror('Ошибка',
        "Первое множество пустое. Из него невозможно удалить точку.")
        return
    
    index = entry_deli1.get()
    try:
        index = int(index)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать номер удаляемой точки первого множества." + 
        ' Ожидалось целое положительное число. Повторите ввод.')
        return
    if (index <= 0):
        box.showerror('Ошибка',
        "Не удалось счиать номер удаляемой точки первого множества." + 
        ' Ожидалось целое положительное число. Повторите ввод.')
        return 
    if (index > n1):
        box.showerror('Ошибка',
        'Точки с таким номером не существует в первом множестве.\
            Повторите ввод.')
        return
    
    dots1.pop(index - 1)
    n1 -= 1
    rewrite_table1()
    rewrite_n1()
    entry_deli1.delete(0, END)  

def ch1():
    global n1
    global dots1 
    
    index = entry_chi1.get()
    try:
        index = int(index)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать номер изменяемой точки первого множества." + 
        ' Ожидалось целое положительное число. Повторите ввод.')
        return
    if (index <= 0):
        box.showerror('Ошибка',
        "Не удалось счиать номер изменяемой точки первого множества." + 
        ' Ожидалось целое положительное число. Повторите ввод.')
        return 
    if (index > n1):
        box.showerror('Ошибка',
        'Точки с таким номером не существует в первом множестве. \
            Повторите ввод.')
        return
    
    x0 = entry_chx1.get()
    try:
        x0 = float(x0)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать координату x изменяемой точки первого множества." + 
        ' Ожидалось вещественное число. Повторите ввод.')
        return 
    y0 = entry_chy1.get()
    try:
        y0 = float(y0)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать координату y изменяемой точки первого множества." + 
        ' Ожидалось вещественное число. Повторите ввод.')
        return 
    dot = {'x' : x0, 'y' : y0}
    dots1[index - 1] = dot
    rewrite_table1()
    entry_chx1.delete(0, END)
    entry_chy1.delete(0, END)
    entry_chi1.delete(0, END)
    

def again1():
    global n1
    global dots1
    n1 = 0
    dots1 = []
    rewrite_n1()
    rewrite_table1()
    disable_dop1()
    disable_table1()
    entry_n1.configure(state = 'normal')
    but_n1.configure(state = 'normal')
    
def disable_dop1():
    entry_addx1.configure(state = 'disable')
    entry_addy1.configure(state = 'disable')
    entry_deli1.configure(state = 'disable')
    entry_chi1.configure(state = 'disable')
    entry_chx1.configure(state = 'disable')
    entry_chy1.configure(state = 'disable')
    but_add1.configure(state = 'disable')
    but_del1.configure(state = 'disable')
    but_ch1.configure(state = 'disable')
    

# операции со вторым множеством
def input_n2():
    global n2
    n2 = entry_n2.get()
    try:
        n2 = int(n2)
    except:
        box.showerror('Ошибка',
        "Количесвто точек должно быть целым неотрицательным числом")
        return
    if n2 < 0:
        box.showerror('Ошибка',
        "Количесвто точек должно быть целым неотрицательным числом")
        return
    entry_n2.configure(state = 'disable')
    but_n2.configure(state = 'disable')
    if (n2 > 10):
        box.showinfo('Внимание',
        "Введите первые 10 точек второго множества через таблицу, а чтобы \
ввести остальные точки, воспользуйтесь опцией 'Добавить'.")
        n2 = 10
        rewrite_n2()
    able_table2(n2)

def able_table2(n):
    for i in range(n):
        entry = entrys_x2[i]
        entry.configure(state = 'normal')
    for i in range(n):
        entry = entrys_y2[i]
        entry.configure(state = 'normal')
    if (n > 0):
        but_dots2.configure(state = 'normal')
    else:
        able_dop2()
        
def input_dots2():
    global n2
    global entrys_x2
    global entrys_y2
    
    x = []
    for i in range(n2):
        x0 = entrys_x2[i].get()
        try:
            x0 = float(x0)
        except:
            box.showerror('Ошибка',
            "Не удалось счиать координату x %d-й точки второго множества."%(
                i + 1) + 
            ' Ожидалось вещественное число. Повторите ввод первой таблицы.')
            return
        else:
            x.append(x0)
    y = []
    for i in range(n2):
        y0 = entrys_y2[i].get()
        try:
            y0 = float(y0)
        except:
            box.showerror('Ошибка',
            "Не удалось счиать координату y %d-й точки второго множества."%(
                i + 1) + 
            ' Ожидалось вещественное число. Повторите ввод первой таблицы.')
            return
        else:
            y.append(y0)     
        
    global dots2
    dots2 = []
    for i in range(n2):
        dot = {'x' : x[i], 'y' : y[i]}
        dots2.append(dot)
        
    rewrite_table2()
    able_dop2()


def able_dop2():
    entry_addx2.configure(state = 'normal')
    entry_addy2.configure(state = 'normal')
    entry_deli2.configure(state = 'normal')
    entry_chi2.configure(state = 'normal')
    entry_chx2.configure(state = 'normal')
    entry_chy2.configure(state = 'normal')
    but_add2.configure(state = 'normal')
    but_del2.configure(state = 'normal')
    but_ch2.configure(state = 'normal')

  
def disable_table2():
    for entry in entrys_x2:
        entry.configure(state = 'disable')
    for entry in entrys_y2:
        entry.configure(state = 'disable')
    but_dots2.configure(state = 'disable')
    
def rewrite_table2():
    able_table2(10)
    clean_table2()
    fill_table2()
    disable_table2()
    
def clean_table2():
    global entrys_x2
    global entrys_y2
    for entry in entrys_x2:
        entry.delete(0, END)
    for entry in entrys_y2:
        entry.delete(0, END)
  
def fill_table2():
    global n2
    global dots2
    for i in range(min(n2, 10)):
        dot = dots2[i]
        entrys_x2[i].insert('insert', '%.2f'%dot['x'])
        entrys_y2[i].insert('insert', '%.2f'%dot['y'])
        
def add2():
    global n2
    global dots2
    x0 = entry_addx2.get()
    try:
        x0 = float(x0)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать координату x добавляемой точки второго множества." + 
        ' Ожидалось вещественное число. Повторите ввод.')
        return 
    y0 = entry_addy2.get()
    try:
        y0 = float(y0)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать координату y добавляемой точки второго множества." + 
        ' Ожидалось вещественное число. Повторите ввод.')
        return 
    n2 += 1
    dot = {'x' : x0, 'y' : y0}
    dots2.append(dot)
    rewrite_table2()
    rewrite_n2()
    entry_addx2.delete(0, END)
    entry_addy2.delete(0, END)

def rewrite_n2():
    global n2
    entry_n2.configure(state = 'normal')
    entry_n2.delete(0, END)
    entry_n2.insert('insert', '%d'%n2)
    entry_n2.configure(state = 'disable')
       
def del2():
    global n2
    global dots2
    
    if (n2 <= 0):
        box.showerror('Ошибка',
        "Второе множество пустое. Из него невозможно удалить точку.")
        return
    
    index = entry_deli2.get()
    try:
        index = int(index)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать номер удаляемой точки второго множества." + 
        ' Ожидалось целое положительное число. Повторите ввод.')
        return
    if (index <= 0):
        box.showerror('Ошибка',
        "Не удалось счиать номер удаляемой точки второго множества." + 
        ' Ожидалось целое положительное число. Повторите ввод.')
        return 
    if (index > n2):
        box.showerror('Ошибка',
        'Точки с таким номером не существует во втором множестве.\
            Повторите ввод.')
        return
    
    dots2.pop(index - 1)
    n2 -= 1
    rewrite_table2()
    rewrite_n2()
    entry_deli2.delete(0, END)  

def ch2():
    global n2
    global dots2
    
    index = entry_chi2.get()
    try:
        index = int(index)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать номер изменяемой точки второго множества." + 
        ' Ожидалось целое положительное число. Повторите ввод.')
        return
    if (index <= 0):
        box.showerror('Ошибка',
        "Не удалось счиать номер изменяемой точки второго множества." + 
        ' Ожидалось целое положительное число. Повторите ввод.')
        return 
    if (index > n2):
        box.showerror('Ошибка',
        'Точки с таким номером не существует во втором множестве.\
            Повторите ввод.')
        return
    
    x0 = entry_chx2.get()
    try:
        x0 = float(x0)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать координату x изменяемой точки второго множества." + 
        ' Ожидалось вещественное число. Повторите ввод.')
        return 
    y0 = entry_chy2.get()
    try:
        y0 = float(y0)
    except:
        box.showerror('Ошибка',
        "Не удалось счиать координату y изменяемой второго первого множества."+ 
        ' Ожидалось вещественное число. Повторите ввод.')
        return 
    dot = {'x' : x0, 'y' : y0}
    dots2[index - 1] = dot
    rewrite_table2()
    entry_chx2.delete(0, END)
    entry_chy2.delete(0, END)
    entry_chi2.delete(0, END)
    

def again2():
    global n2
    global dots2
    n2 = 0
    dots2 = []
    rewrite_n2()
    rewrite_table2()
    disable_dop2()
    disable_table2()
    entry_n2.configure(state = 'normal')
    but_n2.configure(state = 'normal')
    
def disable_dop2():
    entry_addx2.configure(state = 'disable')
    entry_addy2.configure(state = 'disable')
    entry_deli2.configure(state = 'disable')
    entry_chi2.configure(state = 'disable')
    entry_chx2.configure(state = 'disable')
    entry_chy2.configure(state = 'disable')
    but_add2.configure(state = 'disable')
    but_del2.configure(state = 'disable')
    but_ch2.configure(state = 'disable')  
#операции над обоими множествами
def again():
    again1()
    again2()
      
def on_focus(evt):
    global current_entry
    current_entry = evt.widget

#################################################### создание окна  
root = Tk()            
root.title('Решение геометричесской задачи.')       
root.geometry('800x700+10+10')
root.resizable(width=False, height=False)
root['bg'] = ('mint cream')

# заполнение основной панели виджетами
text_task = 'Условие: На плоскости заданы два множества точек. Найти пару \
окружностей, каждая из\n\
которых проходит хотя бы через 3 различные точки одного и того же множества \
(окружности пары\n\
строятся на точках разных множеств) таких, что разность площадей \
четырехугольников, образованных\n\
центрами окружностей, точками касания внутренних общих касательных и точкой \
пересечения касательных,\n\
максимальна. Сделать вывод изображения в графическом режиме.'
lbl_task= Label(root, text=text_task,
    font='arial 11', justify = LEFT, bd = 1, bg = 'LightBlue1')
lbl_task.place(x = 0, y = 0, width = 800, height = 90, anchor= NW)


########################## первое множество
lbl_m1 = Label(root,text = 'Первое множество:',
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_m1.place(x = 100, y = 90, width = 150, height = 20, anchor= NW)

lbl_n1 = Label(root,text = 'Введите количесвто точек:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_n1.place(x = 10, y = 110, width = 200, height = 20, anchor= NW)

entry_n1 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_n1.bind('<FocusIn>', on_focus)
entry_n1.place(x = 210, y = 110, width = 50, height = 20, anchor= NW)

but_n1 = Button(root, text = 'Ввод',font= 'arial 11', justify = LEFT,
                  command = input_n1, bg = 'SteelBlue1')
but_n1.place(x = 265, y = 110, width = 60, height = 20)

lbl_dots1 = Label(root,text = 'Введите координаты точек (вещественные числа):', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_dots1.place(x = 10, y = 130, width = 350, height = 20, anchor= NW)

x0 = 10
x1 = 40
x2 = 100
y0 = 150
m = 0

lbl_i1 = Label(root,text = 'i', 
                  font='arial 11', justify = LEFT, bg = 'mint cream',
                  highlightthickness=1, highlightbackground="black")
lbl_i1.place(x = x0, y = y0+m, width = 30, height = 17, anchor= NW)
lbl_x1 = Label(root,text = 'xi', 
                  font='arial 11', justify = LEFT, bg = 'mint cream',
                  highlightthickness=1, highlightbackground="black")
lbl_x1.place(x = x1, y = y0+m, width = 30, height = 17, anchor= NW)
lbl_y1 = Label(root,text = 'yi', 
                  font='arial 11', justify = LEFT, bg = 'mint cream',
                  highlightthickness=1, highlightbackground="black")
lbl_y1.place(x = x2, y = y0+m, width = 30, height = 17, anchor= NW)
for i in range(10):
    m += 18
    lbl_i = Label(root,text = '%d'%(i+1), 
                  font='arial 11', justify = LEFT, bg = 'mint cream',
                  highlightthickness=1, highlightbackground="black")
    lbl_i.place(x = x0, y = y0+m, width = 30, height = 15, anchor= NW)
    entry_x = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
    entry_x.bind('<FocusIn>', on_focus)
    entry_x.place(x = x1, y = y0+m, width = 50, height = 15, anchor= NW)
    entrys_x1.append(entry_x)
    entry_y = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
    entry_y.bind('<FocusIn>', on_focus)
    entry_y.place(x = x2, y = y0+m, width = 50, height = 15, anchor= NW)
    entrys_y1.append(entry_y)
    
    
but_dots1 = Button(root, text = 'Ввод',font= 'arial 11', justify = LEFT,
                  command = input_dots1, bg = 'SteelBlue1')
but_dots1.place(x = x2 + 70, y = y0+m, width = 60, height = 20)
    
lbl_add1 = Label(root,text = 'Добавление точки:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_add1.place(x = 10, y = 380, width = 150, height = 20, anchor= NW)

lbl_addx1 = Label(root,text = 'x:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_addx1.place(x = 30, y = 400, width = 40, height = 20, anchor= NW)

entry_addx1 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_addx1.bind('<FocusIn>', on_focus)
entry_addx1.place(x = 60, y = 400, width = 50, height = 20, anchor= NW)

lbl_addy1 = Label(root,text = 'y:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_addy1.place(x = 120, y = 400, width = 40, height = 20, anchor= NW)

entry_addy1 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_addy1.bind('<FocusIn>', on_focus)
entry_addy1.place(x = 150, y = 400, width = 50, height = 20, anchor= NW)

but_add1 = Button(root, text = 'Добавить',font= 'arial 11', justify = LEFT,
                  command = add1, bg = 'SteelBlue1')
but_add1.place(x = 220, y = 400, width = 80, height = 20)

lbl_del1 = Label(root,text = 'Удаление точки:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_del1.place(x = 10, y = 430, width = 140, height = 20, anchor= NW)

lbl_deli1 = Label(root,text = 'номер точки:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_deli1.place(x = 30, y = 450, width = 150, height = 20, anchor= NW)

entry_deli1 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_deli1.bind('<FocusIn>', on_focus)
entry_deli1.place(x = 160, y = 450, width = 50, height = 20, anchor= NW)

but_del1 = Button(root, text = 'Удалить',font= 'arial 11', justify = LEFT,
                  command = del1, bg = 'SteelBlue1')
but_del1.place(x = 220, y = 450, width = 80, height = 20)

lbl_ch1 = Label(root,text = 'Изменение точки:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_ch1.place(x = 10, y = 480, width = 150, height = 20, anchor= NW)

lbl_chi1 = Label(root,text = 'номер точки:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_chi1.place(x = 30, y = 500, width = 150, height = 20, anchor= NW)

entry_chi1 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_chi1.bind('<FocusIn>', on_focus)
entry_chi1.place(x = 160, y = 500, width = 50, height = 20, anchor= NW)

lbl_chx1 = Label(root,text = 'новые x:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_chx1.place(x = 10, y = 525, width = 100, height = 20, anchor= NW)

entry_chx1 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_chx1.bind('<FocusIn>', on_focus)
entry_chx1.place(x = 90, y = 525, width = 50, height = 20, anchor= NW)

lbl_chy1 = Label(root,text = 'y:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_chy1.place(x = 140, y = 525, width = 40, height = 20, anchor= NW)

entry_chy1 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_chy1.bind('<FocusIn>', on_focus)
entry_chy1.place(x = 170, y = 525, width = 50, height = 20, anchor= NW)

but_ch1 = Button(root, text = 'Изменить',font= 'arial 11', justify = LEFT,
                  command = ch1, bg = 'SteelBlue1')
but_ch1.place(x = 230, y = 525, width = 80, height = 20)

########################## второе множество
STEPX = 400
lbl_m2 = Label(root,text = 'Второе множество:',
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_m2.place(x = 100+STEPX, y = 90, width = 150, height = 20, anchor= NW)

lbl_n2 = Label(root,text = 'Введите количесвто точек:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_n2.place(x = 10+STEPX, y = 110, width = 200, height = 20, anchor= NW)

entry_n2 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_n2.bind('<FocusIn>', on_focus)
entry_n2.place(x = 210+STEPX, y = 110, width = 50, height = 20, anchor= NW)

but_n2 = Button(root, text = 'Ввод',font= 'arial 11', justify = LEFT,
                  command = input_n2, bg = 'SteelBlue1')
but_n2.place(x = 265+STEPX, y = 110, width = 60, height = 20)

lbl_dots2 = Label(root,text = 'Введите координаты точек (вещественные числа):', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_dots2.place(x = 10+STEPX, y = 130, width = 350, height = 20, anchor= NW)

x0 = 10+STEPX
x1 = 40+STEPX
x2 = 100+STEPX
y0 = 150
m = 0

lbl_i2 = Label(root,text = 'i', 
                  font='arial 11', justify = LEFT, bg = 'mint cream',
                  highlightthickness=1, highlightbackground="black")
lbl_i2.place(x = x0, y = y0+m, width = 30, height = 17, anchor=NW)
lbl_x2 = Label(root,text = 'xi', 
                  font='arial 11', justify = LEFT, bg = 'mint cream',
                  highlightthickness=1, highlightbackground="black")
lbl_x2.place(x = x1, y = y0+m, width = 30, height = 17, anchor= NW)
lbl_y2 = Label(root,text = 'yi', 
                  font='arial 11', justify = LEFT, bg = 'mint cream',
                  highlightthickness=1, highlightbackground="black")
lbl_y2.place(x = x2, y = y0+m, width = 30, height = 17, anchor= NW)
for i in range(10):
    m += 18
    lbl_i = Label(root,text = '%d'%(i+1), 
                  font='arial 11', justify = LEFT, bg = 'mint cream',
                  highlightthickness=1, highlightbackground="black")
    lbl_i.place(x = x0, y = y0+m, width = 30, height = 15, anchor= NW)
    entry_x = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
    entry_x.bind('<FocusIn>', on_focus)
    entry_x.place(x = x1, y = y0+m, width = 50, height = 15, anchor= NW)
    entrys_x2.append(entry_x)
    entry_y = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
    entry_y.bind('<FocusIn>', on_focus)
    entry_y.place(x = x2, y = y0+m, width = 50, height = 15, anchor= NW)
    entrys_y2.append(entry_y)
    
    
but_dots2 = Button(root, text = 'Ввод',font= 'arial 11', justify = LEFT,
                  command = input_dots2, bg = 'SteelBlue1')
but_dots2.place(x = x2 + 70, y = y0+m, width = 60, height = 20)
    
lbl_add2 = Label(root,text = 'Добавление точки:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_add2.place(x = 10+STEPX, y = 380, width = 150, height = 20, anchor= NW)

lbl_addx2 = Label(root,text = 'x:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_addx2.place(x = 30+STEPX, y = 400, width = 40, height = 20, anchor= NW)

entry_addx2 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_addx2.bind('<FocusIn>', on_focus)
entry_addx2.place(x = 60+STEPX, y = 400, width = 50, height = 20, anchor= NW)

lbl_addy2 = Label(root,text = 'y:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_addy2.place(x = 120+STEPX, y = 400, width = 40, height = 20, anchor= NW)

entry_addy2 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_addy2.bind('<FocusIn>', on_focus)
entry_addy2.place(x = 150+STEPX, y = 400, width = 50, height = 20, anchor= NW)

but_add2 = Button(root, text = 'Добавить',font= 'arial 11', justify = LEFT,
                  command = add2, bg = 'SteelBlue1')
but_add2.place(x = 220+STEPX, y = 400, width = 80, height = 20)

lbl_del2 = Label(root,text = 'Удаление точки:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_del2.place(x = 10+STEPX, y = 430, width = 140, height = 20, anchor= NW)

lbl_deli2 = Label(root,text = 'номер точки:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_deli2.place(x = 30+STEPX, y = 450, width = 150, height = 20, anchor= NW)

entry_deli2 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_deli2.bind('<FocusIn>', on_focus)
entry_deli2.place(x = 160+STEPX, y = 450, width = 50, height = 20, anchor= NW)

but_del2 = Button(root, text = 'Удалить',font= 'arial 11', justify = LEFT,
                  command = del2, bg = 'SteelBlue1')
but_del2.place(x = 220+STEPX, y = 450, width = 80, height = 20)

lbl_ch2 = Label(root,text = 'Изменение точки:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_ch2.place(x = 10+STEPX, y = 480, width = 150, height = 20, anchor= NW)

lbl_chi2 = Label(root,text = 'номер точки:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_chi2.place(x = 30+STEPX, y = 500, width = 150, height = 20, anchor= NW)

entry_chi2 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_chi2.bind('<FocusIn>', on_focus)
entry_chi2.place(x = 160+STEPX, y = 500, width = 50, height = 20, anchor= NW)

lbl_chx2 = Label(root,text = 'новые x:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_chx2.place(x = 10+STEPX, y = 525, width = 100, height = 20, anchor= NW)

entry_chx2 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_chx2.bind('<FocusIn>', on_focus)
entry_chx2.place(x = 90+STEPX, y = 525, width = 50, height = 20, anchor= NW)

lbl_chy2 = Label(root,text = 'y:', 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_chy2.place(x = 140+STEPX, y = 525, width = 40, height = 20, anchor= NW)

entry_chy2 = Entry(root, justify = LEFT,
                      font='arial 11', bg = "CadetBlue1")
entry_chy2.bind('<FocusIn>', on_focus)
entry_chy2.place(x = 170+STEPX, y = 525, width = 50, height = 20, anchor= NW)

but_ch2 = Button(root, text = 'Изменить',font= 'arial 11', justify = LEFT,
                  command = ch2, bg = 'SteelBlue1')
but_ch2.place(x = 230+STEPX, y = 525, width = 80, height = 20)

but_again1 = Button(root, text = 'Сбросить 1 множество',font= 'arial 11', 
                    justify = LEFT,
                  command = again1, bg = 'SteelBlue1')
but_again1.place(x = 10, y = 560, width = 200, height = 20)

but_again2 = Button(root, text = 'Сбросить 2 множество',font= 'arial 11', 
                    justify = LEFT,
                  command = again2, bg = 'SteelBlue1')
but_again2.place(x = 550, y = 560, width = 200, height = 20)

but_solve = Button(root, text = 'Решить',font= 'arial 13', justify = LEFT,
                  command = lambda: solve(dots1, dots2), bg = 'SteelBlue1')

but_solve.place(x = 250, y = 600, width = 80, height = 30)

but_again = Button(root, text = 'Сбросить все',font= 'arial 13', 
                   justify = LEFT,
                  command = again, bg = 'SteelBlue1')
but_again.place(x = 400, y = 600, width = 150, height = 30)

text_about = 'Примечание: через таблицу можно ввести не более 10 \
точек каждого \nмножества. Чтобы ввести 11 точек и более, \
воспользуйтесь опцией "Добавить".'
lbl_about = Label(root,text = text_about, 
    font='arial 11', justify = LEFT, bg = 'mint cream')
lbl_about.place(x = 10, y = 650, width = 560, height = 40, anchor= NW)

again()
root.mainloop()
