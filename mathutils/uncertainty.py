# from custom_utils.science.imports import *
import scipy as sp
from custom_utils.math import partial_derivative


def up_function(f, arguments, arg_uncertainties):

    f_uncertainty_sqr = 0

    for i in range(len(arguments)):
        partial = partial_derivative(f, i, arguments)
        f_uncertainty_sqr += partial**2 * arg_uncertainties[i]**2

    return sp.sqrt(f_uncertainty_sqr)


def up_add(u1, u2):

    return sp.sqrt(u1**2 + u2**2)


def up_multiply(v1, v2, u1, u2):

    return sp.sqrt((v2 * u1)**2 + (v1 * u2)**2)


def main():

    def fce(a, b, c):

        return sp.sin(a) + sp.cos(b) + 2 * sp.sin(c)

    p = up_function(fce, [1, 2, 3], [0.1, 0.2, 0.3])
    print(p)


if __name__ == '__main__':
    main()
