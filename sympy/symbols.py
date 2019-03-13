import sympy as sym
import string

symbol_names = list(string.ascii_letters)
symbol_names += [f"s{n}" for n in range(10)]
symbol_names += [f"x{n}" for n in range(10)]
symbol_names += [f"y{n}" for n in range(10)]
symbol_names += [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "eta",
    "theta",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "xi",
    "omicron",
    "pi",
    "rho",
    "sigma",
    "tau",
    "upsilon",
    "phi",
    "chi",
    "psi",
    "omega"
]

for symbol in symbol_names:
    globals()[f"s_{symbol}"] = sym.symbols(symbol)

del symbol_names, string
