"""
модуль предназначен для решения уравнений любого вида
"""
import asdf
from pydoc import locate
from sympy import solve, Eq


class Equal:
    """
    класс предназначен для решения уравнений любого вида
    """
    @staticmethod
    def equal(valid_text):
        """
        метод решения уравнений
        :param valid_text: исходное уравнение
        :return: список корней
        """
        solution = None
        if 'x' in valid_text and '=' in valid_text:
            t_locate = locate('sympy.sympify')
            lhs = valid_text.rsplit('=', 1)[0]
            lhs = t_locate(lhs)
            rhs = valid_text.rsplit('=', 1)[1]
            rhs = t_locate(rhs)
            solution = solve(Eq(lhs, rhs), 'x')
        if solution is None:
            solution = 'any number'
        return solution

    @staticmethod
    def check_result(left, right, variable):
        """
        метод получения списка корней для их поверки
        :param left: левая часть уравнения
        :param right: правая часть уравнения
        :param variable: имя неизвестного
        :return:
        """
        t_locate = locate('sympy.sympify')
        return solve(Eq(t_locate(left), t_locate(right)), variable)
