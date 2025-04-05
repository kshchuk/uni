import sympy as sp
import itertools


def divisors(n):
    """
    Повертає множину всіх цілих дільників числа n (як позитивних, так і негативних).
    """
    n = abs(n)
    divs = set()
    for i in range(1, n + 1):
        if n % i == 0:
            divs.add(i)
            divs.add(-i)
    return divs


def lagrange_interpolation(xs, ys, x):
    """
    Обчислює інтерполяційний многочлен Лагранжа, який проходить через точки (xs[i], ys[i]).
    Повертає розширений вираз многочлена.
    """
    poly = 0
    n = len(xs)
    for i in range(n):
        term = ys[i]
        for j in range(n):
            if j != i:
                term *= (x - xs[j]) / (xs[i] - xs[j])
        poly += term
    return sp.expand(poly)


def polynomial_divides(P, Q, x):
    """
    Перевіряє, чи ділиться многочлен P на Q без остачі.
    Повертає кортеж (True, quotient) якщо ділиться, інакше (False, None).
    """
    quotient, remainder = sp.div(P, Q, domain='QQ')
    if sp.simplify(remainder) == 0:
        return True, sp.expand(quotient)
    else:
        return False, None


def kronecker_factor(P, x):
    """
    Шукає нетривіальний дільник многочлена P (якщо він існує) методом Кронекера.
    Працює для потенційних дільників степеня m, де 1 <= m <= floor(degree(P)/2).
    Якщо знаходить дільник g(x) та частку Q(x) так, що P(x) = g(x)*Q(x),
    повертає (g(x), Q(x)); інакше повертає (None, None).
    """
    n = sp.degree(P, x)
    # Перебираємо можливі степені dільника m від 1 до floor(n/2)
    for m in range(1, n // 2 + 1):
        # Обчислюємо значення P(i) для i = 0,1,..., m
        values = [P.subs(x, i) for i in range(m + 1)]
        # Для кожного i знаходимо множину дільників P(i)
        U = [list(divisors(int(v))) if v != 0 else [0] for v in values]
        # Перебір усіх можливих комбінацій (g(0), g(1), ..., g(m))
        for candidate in itertools.product(*U):
            xs = list(range(m + 1))
            # Обчислюємо інтерполяційний многочлен g(x)
            g_expr = lagrange_interpolation(xs, candidate, x)
            g_poly = sp.Poly(g_expr, x)
            # Розглядаємо лише випадки, коли ступінь g(x) дорівнює m (і g(x) не константа)
            if g_poly.degree() != m or m == 0:
                continue
            # Перевіряємо, чи мають усі коефіцієнти многочлена цілі значення
            coeffs = g_poly.all_coeffs()
            if all(coef.is_integer for coef in coeffs):
                # Перевіряємо, чи ділить g(x) P(x)
                divides, Q = polynomial_divides(P, g_poly.as_expr(), x)
                if divides and sp.degree(Q, x) < n:
                    return g_poly.as_expr(), Q
    return None, None


def kronecker_factorization(P, x):
    """
    Рекурсивно розкладає многочлен P на множники за методом Кронекера.
    Якщо P не розкладається (є неприводимим), повертає [P].
    """
    factors = []
    # Якщо P є константою або має нульовий степінь, повертаємо його
    if sp.degree(P, x) <= 0:
        return [P]
    factor, quotient = kronecker_factor(P, x)
    if factor is None:
        # Якщо не знайдено дільника, вважаємо P неприводимим
        return [P]
    else:
        # Рекурсивно розкладаємо знайдений множник та частку
        factors += kronecker_factorization(factor, x)
        factors += kronecker_factorization(quotient, x)
        return factors


if __name__ == "__main__":
    # Оголошення символу
    x = sp.symbols('x')

    # завдання №8
    P1 = 16 * x ** 4 + 76 * x ** 3 + 68 * x ** 2 - 76 * x - 84
    print("Многочлен P1:")
    sp.pprint(P1)
    factors1 = kronecker_factorization(P1, x)
    print("\nЗнайдені множники для P1 методом Кронекера:")
    for f in factors1:
        sp.pprint(f)
    print("\nПеревірка: добуток множників:")
    sp.pprint(sp.expand(sp.Mul(*factors1)))

    # завдання №28
    P2 = x ** 4 + 2 * x ** 3 - 72 * x ** 2 - 416 * x - 640
    print("\nМногочлен P2:")
    sp.pprint(P2)
    factors2 = kronecker_factorization(P2, x)
    print("\nЗнайдені множники для P2 методом Кронекера:")
    for f in factors2:
        sp.pprint(f)
    print("\nПеревірка: добуток множників:")
    sp.pprint(sp.expand(sp.Mul(*factors2)))
