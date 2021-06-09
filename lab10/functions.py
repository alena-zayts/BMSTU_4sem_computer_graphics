from math import sin, cos


def func1(x, z):
    y = sin(x) ** 2 + cos(z) ** 2  # вычислили y
    return y


def func2(x, z):
    y = sin(x * z) - cos(x * z)
    return y


def func3(x, z):
    y = cos(x) * sin(z)
    return y


def func4(x, z):
    y = 1 / (1 + x ** 2) + 1 / (1 + z ** 2)
    return y


def func5(x, z):
    y = x / 2 + z / 2
    return y


funcs_list = list()
funcs_list.append(func1)
funcs_list.append(func2)
funcs_list.append(func3)
funcs_list.append(func4)
funcs_list.append(func5)


