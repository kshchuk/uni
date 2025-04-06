import sympy
from sympy.polys.domains import QQ
from sympy.polys.rings import ring
from sympy.polys.groebnertools import _buchberger

# Оголошуємо змінні для sympy.groebner
x, y, z = sympy.symbols('x y z', real=True)

# Записуємо наші три поліноми як символьні вирази
f1 = x*y + z - 1
f2 = x - y - z**2
f3 = x**2 - 2*y + 1

# Обчислення редукованого базису Гребнера за допомогою sympy.groebner
G_reduced = sympy.groebner([f1, f2, f3], x, y, z, order='lex')
print("Reduced Gröbner basis (sympy.groebner):")
print(G_reduced)

# Для обчислення "звичайного" (не редукованого) базису використаємо алгоритм Бухбергерга.
# Створюємо кільце змінних над полем раціональних чисел.
R, xR, yR, zR = ring('x, y, z', QQ, order='lex')
# Перетворюємо наші поліноми у вигляді елементів кільця R:
F = [xR*yR + zR - 1, xR - yR - zR**2, xR**2 - 2*yR + 1]

# Обчислюємо базис Гребнера за алгоритмом Бухбергерга (цей базис не редукується автоматично)
B_non_reduced = _buchberger(F, R)
print("\nNon-reduced Gröbner basis (buchberger):")
for poly in B_non_reduced:
    print(poly)
