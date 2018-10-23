import sympy as smp
import string

symbol_names = list(string.ascii_letters)
symbol_names += [f"s{n}" for n in range(10)]
symbol_names += [f"x{n}" for n in range(10)]
symbol_names += [f"y{n}" for n in range(10)]

for symbol in symbol_names:
    globals()[f"s_{symbol}"] = smp.symbols(symbol)

del symbol_names, string
