from math import *


class Integral:
    @staticmethod
    def f(expr, x):
        return eval(expr)

    @staticmethod
    def integral(a, b, expr, n=8):
        h = (b-a)/n
        n //= 2
        result = (Integral.f(expr, a) + Integral.f(expr, a + 2 * n * h))
        for i in range(1, n):
            result += 2 * Integral.f(expr, a + h * 2 * i)
        for i in range(1, n + 1):
            result += 4 * Integral.f(expr, a + h * 2 * i - h)
        result *= h / 3
        return round(result, 5)
