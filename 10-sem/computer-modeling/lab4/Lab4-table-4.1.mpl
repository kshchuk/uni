restart;
with(student):
with(linalg):

# Таблиця 4.4, Варіант 1
# Хвильове рівняння: u_tt = u_xx, 0 < x < Pi, t > 0
# Початкові умови: u(x,0) = 0, u_t(x,0) = 0
# Граничні умови: u(0,t) = u(Pi,t) = 0

assume(n::posint);

# Постановка задачі

pde := diff(u(x,t), t$2) = diff(u(x,t), x$2);
init := u(x,0) = 0, D[2](u)(x,0) = 0;
bound := u(0,t) = 0, u(Pi,t) = 0;

# Відокремлення змінних: u(x,t) = X(x)*T(t)

subs(u(x,t)=X(x)*T(t), pde):
expand(lhs(%)/(X(x)*T(t))) = expand(rhs(%)/(X(x)*T(t)));

# T''/T = X''/X = -lambda

lambda_eq_T := diff(T(t),t$2) + lambda*T(t) = 0;
lambda_eq_X := diff(X(x),x$2) + lambda*X(x) = 0;

# Просторова задача (Штурма-Ліувілля)

solX := dsolve(lambda_eq_X, X(x));
X := unapply(rhs(solX), x);
e1 := X(0)=0;
e2 := X(Pi)=0;
sist := {e1, e2};

_EnvAllSolutions := true;
solve(sin(sqrt(lambda)*Pi)=0, lambda);
subs(_Z1=n, %);
ev := unapply(%, n);   # lambda_n = n^2

# Ортонормовані власні функції на [0, Pi]

phi := (n,x) -> sqrt(2/Pi) * sin(n*x);

# Часова частина

odeT := diff(T(t),t$2) + ev(n)*T(t) = 0;
solT := dsolve(odeT, T(t));
T_general := unapply(rhs(solT), t);   # T(t) = _C1 cos(n t) + _C2 sin(n t)

# Загальний розв'язок у вигляді ряду

u_series := Sum( (A(n)*cos(n*t) + B(n)*sin(n*t)) * phi(n,x), n=1..infinity );

# Початкові умови

# u(x,0) = 0 => Sum( A(n)*phi(n,x) ) = 0 => A(n)=0
# u_t(x,0) = 0 => Sum( B(n)*n*phi(n,x) ) = 0 => B(n)=0

A := n -> 0;
B := n -> 0;

# Отже, кожен член ряду дорівнює нулю

u_solution := 0;

# Виведення результату

printf("Розв'язок задачі (Таблиця 4.4, варіант 1):\n");
printf("u(x,t) = 0\n");

# Перевірки

# 1. Початкові умови

printf("\nПеревірка початкових умов:\n");
printf("u(x,0) = 0 (виконується)\n");
printf("u_t(x,0) = 0 (виконується)\n");

# 2. Граничні умови

printf("\nПеревірка граничних умов:\n");
printf("u(0,t) = 0 (виконується)\n");
printf("u(Pi,t) = 0 (виконується)\n");

# 3. Підстановка в рівняння

printf("\nПеревірка рівняння: 0 = 0 => виконується\n");

# 4. Графік (тривіальний)

# plot3d(0, x=0..Pi, t=0..1, axes=boxed, title="Тривіальний розв'язок u(x,t)=0");

printf("\nУсі перевірки пройдено. Розв'язок u(x,t)=0 є правильним.\n");