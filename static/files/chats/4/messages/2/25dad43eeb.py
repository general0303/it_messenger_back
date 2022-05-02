from numpy import matrix
from numpy import linalg
from numpy import round


class Matrix:
    @staticmethod
    def addition(a, b):
        return (matrix(a)+matrix(b)).tolist()

    @staticmethod
    def multiplication_on_number(a, b):
        return (matrix(a)*b).tolist()

    @staticmethod
    def multiplication(a, b):
        return (matrix(a)*matrix(b)).tolist()

    @staticmethod
    def transposition(a):
        return matrix(a).T.tolist()

    @staticmethod
    def get_matrix_determinant(a):
        return round(linalg.det(matrix(a)), 10)

    @staticmethod
    def get_invert_matrix(a):
        return round(linalg.inv(matrix(a)), 10).tolist()
