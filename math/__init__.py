from scipy.misc import derivative as _derivative


def partial_derivative(f, with_respect_to, arguments, n=1, dx=1e-6):
    """
    Calculates partial derivative of function f(a1, a2, a3,...) with respect to 
    argument in position given by with_respect_to.

    Parameters
    ----------
    f : callable, N arguments
        function to differentiate
    with_respect_to : int in range(0, N)
        position of the argument with respect to which f should be differentiated
    arguments : N-sequence
        arguments to f
    n : int
    dx : float
    """

    arguments_list = list(arguments)

    def helper(arg):
        """ is the f function with only the argument of interest exposed """

        arguments_with_val = arguments_list[:with_respect_to] \
            + [arg] \
            + arguments_list[with_respect_to + 1:]
        return f(*arguments_with_val)

    if helper(arguments[with_respect_to]) is None:
        raise Exception("f doesn't have a return value")

    return _derivative(helper, arguments[with_respect_to], n=n, dx=dx)
