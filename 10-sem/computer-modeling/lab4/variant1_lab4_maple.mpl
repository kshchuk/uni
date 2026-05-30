restart;
with(student):
with(linalg):

# =========================================================
# ЛАБОРАТОРНА РОБОТА 4
# Варіант 1
#
# Ярослав Кіщук
# =========================================================


# =========================================================
# ТАБЛИЦЯ 4.1
# Однорідне рівняння теплопровідності
# =========================================================

eq_heat :=
diff(u(x,t),t)-a^2*diff(u(x,t),x,x)=0:

init_heat :=
u(x,0)=phi(x):

bound_heat :=
u(0,t)=0,
u(L,t)=0:

phi :=
x->c*x*(L-x)/L^2:

# Відокремлення змінних

subs(u(x,t)=X(x)*T(t),eq_heat):

expand(lhs(%)/(X(x)*T(t)))=0:

s1_heat :=
op(1,lhs(%))=-lambda:

s2_heat :=
op(2,lhs(%))=lambda:

# Просторова задача

assume(lambda>0):

dsolve(s2_heat,X(x));

X :=
unapply(rhs(%),x):

e1 :=
X(0)=0:

e2 :=
X(L)=0:

sist :=
{e1,e2}:

A :=
genmatrix(sist,{_C1,_C2}):

Delta :=
convert(det(A),trig):

_EnvAllSolutions:=true:

solve(Delta,lambda);

subs(_Z1='k',%):

ev :=
unapply(%,k):

# Власні функції

X:='X':

assume(k,posint):

subs(lambda=ev(k),s2_heat);

dsolve({%,X(0)=0,X(L)=0},X(x));

rhs(%)
/sqrt(int(rhs(%)^2,x=0..L));

simplify(%,radical,symbolic):

ef :=
unapply(%,(k,x)):

# Часова частина

eqT :=
subs(lambda=ev(k),s1_heat):

dsolve(eqT,T(t));

# Загальний розв'язок

U :=
(x,t)->
Sum(
C(k)*
exp(-a^2*ev(k)*t)*
ef(k,x),
k=1..infinity
):

U(x,t);

# Коефіцієнти ряду

assume(L>0):

Ck :=
Int(phi(x)*ef(k,x),x=0..L):

Ck :=
value(Ck):

C :=
unapply(Ck,k):

# Остаточний розв'язок

sol_heat :=
u(x,t)=U(x,t);

sol_heat;


# =========================================================
# ТАБЛИЦЯ 4.2
# Хвильове рівняння
# =========================================================

restart;
with(student):
with(linalg):

eq_wave :=
diff(u(x,t),t,t)-v^2*diff(u(x,t),x,x)=0:

init_wave :=
u(x,0)=0,
D[2](u)(x,0)=psi(x):

psi :=
x->x:

bound_wave :=
u(0,t)=0,
u(L,t)=0:

# Відокремлення змінних

subs(u(x,t)=X(x)*T(t),eq_wave):

expand(lhs(%)/(X(x)*T(t)))=0:

s1_wave :=
op(1,lhs(%))=-lambda:

s2_wave :=
op(2,lhs(%))=lambda:

# Просторова задача

assume(lambda>0):

dsolve(s2_wave,X(x));

X :=
unapply(rhs(%),x):

e1 :=
X(0)=0:

e2 :=
X(L)=0:

sist :=
{e1,e2}:

A :=
genmatrix(sist,{_C1,_C2}):

Delta :=
convert(det(A),trig):

_EnvAllSolutions:=true:

solve(Delta,lambda);

subs(_Z1='k',%):

ev :=
unapply(%,k):

# Власні функції

X:='X':

assume(k,posint):

subs(lambda=ev(k),s2_wave);

dsolve({%,X(0)=0,X(L)=0},X(x));

rhs(%)
/sqrt(int(rhs(%)^2,x=0..L));

simplify(%,radical,symbolic):

ef :=
unapply(%,(k,x)):

# Часова частина

eqT :=
subs(lambda=ev(k),s1_wave);

dsolve(eqT,T(t));

# Формування ряду

spr :=
Sum(
C(k)*
sin(sqrt(ev(k))*v*t)*
ef(k,x),
k=1..infinity
):

spr;

# Коефіцієнти

value(subs(t=0,diff(spr,t))=psi(x));

Ck :=
Int(
psi(x)*ef(k,x),
x=0..L
)/(sqrt(ev(k))*v):

assume(L>0):

Ck :=
simplify(value(Ck)):

C :=
unapply(Ck,k):

# Остаточний розв'язок

solution :=
subs(C(k)=C(k),spr):

solution;


# =========================================================
# РІВНЯННЯ ТЕПЛОМАСОПЕРЕНОСУ
# =========================================================

restart;
with(student):
with(linalg):

eq_tm :=
diff(u(x,t),t)
-diff(u(x,t),x,x)
+u(x,t)=0:

init_tm :=
u(x,0)=1:

bound_tm :=
u(0,t)=0,
u(g,t)=0:

subs(u(x,t)=X(x)*T(t),eq_tm):

expand(lhs(%)/(X(x)*T(t)))=0:

s1_tm :=
op(1,lhs(%))=-lambda:

s2_tm :=
op(2,lhs(%))=lambda:

assume(lambda>0):

dsolve(s2_tm,X(x));

X :=
unapply(rhs(%),x):

e1 :=
X(0)=0:

e2 :=
X(g)=0:

sist :=
{e1,e2}:

A :=
genmatrix(sist,{_C1,_C2}):

Delta :=
convert(det(A),trig):

_EnvAllSolutions:=true:

solve(Delta,lambda);

subs(_Z1='k',%):

ev :=
unapply(%,k):

X:='X':

assume(k,posint):

subs(lambda=ev(k),s2_tm);

dsolve({%,X(0)=0,X(g)=0},X(x));

rhs(%)
/sqrt(int(rhs(%)^2,x=0..g));

simplify(%,radical,symbolic):

ef :=
unapply(%,(k,x)):

U :=
(x,t)->
Sum(
C(k)*
exp(-(ev(k)+1)*t)*
ef(k,x),
k=1..infinity
):

sol_tm :=
u(x,t)=U(x,t);

sol_tm;