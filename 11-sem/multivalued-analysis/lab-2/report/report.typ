// Звіт до лаб. №2 «Проблеми багатозначного аналізу», варіант 15.

#let subject = [Проблеми багатозначного аналізу]
#let lab = [Лабораторна робота 2]
#let R = json("figures/results.json")

#set document(title: "ПБА. Лабораторна робота 2", author: "Кіщук Ярослав Ярославович")
#set text(lang: "uk", font: "New Computer Modern", size: 11pt)
#set par(justify: true, leading: 0.95em, spacing: 1.1em, first-line-indent: 1.5em)
#set page(paper: "a4", margin: (x: 2.5cm, top: 2.6cm, bottom: 2.4cm))

#set heading(numbering: "1.1")
#show heading.where(level: 1): set text(size: 16pt, weight: "regular")
#show heading.where(level: 2): set text(size: 12.5pt)
#show heading.where(level: 1): it => {
  set text(weight: "regular")
  block(above: 2em, below: 1.2em)[#if it.numbering != none [#counter(heading).display(it.numbering)#h(1em)]#it.body]
}
#show heading.where(level: 2): it => {
  block(above: 1.6em, below: 1em)[#if it.numbering != none [#counter(heading).display(it.numbering)#h(1em)]#it.body]
}

#set math.equation(numbering: "(1)")
#show ref: it => {
  let el = it.element
  if el != none and el.func() == math.equation {
    link(el.location(), numbering("(1)", ..counter(math.equation).at(el.location())))
  } else if el != none and el.func() == figure {
    // у тексті посилання з малої літери: «рис. 3», «табл. 2»
    let sup = if el.kind == image [рис.] else [табл.]
    link(el.location(), [#sup~#numbering(el.numbering, ..el.counter.at(el.location()))])
  } else { it }
}
#set figure(gap: 0.9em)
#show figure.where(kind: image): set figure(supplement: [Рис.])
#show figure.where(kind: table): set figure(supplement: [Табл.])
#set figure.caption(separator: [: ])
#show figure.where(kind: table): set figure.caption(position: top)
#show figure: set block(above: 1.4em, below: 1.4em)

#show raw: set text(font: "DejaVu Sans Mono", size: 8.4pt)
#show raw.where(block: true): set text(size: 7.6pt)
#show raw.where(block: true): set par(leading: 0.55em)
#show raw.where(block: true): it => block(width: 100%, inset: (left: 0.5em), it)
#show table: set par(justify: false)
#set list(indent: 1em, spacing: 1em)
#set enum(indent: 1em, spacing: 1em)

// Таблиця: товсті лінії зверху й знизу, лінія під шапкою, вертикальні між колонками.
#let tbl(cols, align: center + horizon, ..cells) = table(
  columns: cols, inset: (x: 6pt, y: 5pt), align: align,
  stroke: (x, y) => (
    top: if y == 0 { 1pt } else if y == 1 { 0.6pt } else { 0pt },
    left: if x > 0 { 0.4pt } else { 0pt },
  ),
  ..cells,
  table.hline(stroke: 1pt),
)
#let fig(f, w, cap) = figure(image("figures/" + f, width: w), caption: cap)

// Цитата з джерела: текст оригіналу, (необов'язково) переклад і точне місце в джерелі.
#let srcq(from, body, tr: none) = block(
  width: 100%, inset: (left: 0.9em, right: 0.3em, y: 0.45em), above: 1.1em, below: 1.1em,
  stroke: (left: 1.2pt + luma(150)),
)[
  #set par(first-line-indent: 0pt, leading: 0.8em, spacing: 0.7em)
  #set text(size: 10pt)
  #set math.equation(numbering: none)  // у цитатах -- лише номери формул джерела
  #body
  #if tr != none {
    parbreak()
    set text(fill: luma(70))
    [_Переклад:_ #tr]
  }
  #align(right, text(9.5pt, fill: luma(90))[-- #from])
]

// Форматування чисел з results.json
#let fix(v, d) = {
  let s = str(calc.round(v, digits: d))
  if not s.contains(".") { s += "." }
  let p = s.split(".")
  let neg = p.at(0).starts-with("-") or p.at(0).starts-with("−")
  $#(p.at(0) + "." + p.at(1) + "0" * (d - p.at(1).len()))$
}
#let sci(v, d: 2) = {
  if v == 0 { return $0$ }
  let e = calc.floor(calc.log(calc.abs(v), base: 10))
  let m = calc.round(v / calc.pow(10.0, e), digits: d)
  if calc.abs(m) >= 10 { m = m / 10; e += 1 }
  let ms = if d == 0 { str(int(m)) } else {
    let p = (str(m) + if str(m).contains(".") { "" } else { "." }).split(".")
    p.at(0) + "." + p.at(1) + "0" * (d - p.at(1).len())
  }
  if e == 0 { $#ms$ } else { $#ms dot 10^(#str(e))$ }
}
#let vec3(v, d) = $(#fix(v.at(0), d), #fix(v.at(1), d), #fix(v.at(2), d))$

// Таблиця значень відображення X(t_k) = E(x(t_k), Q(t_k))
#let values-table(rows) = text(9.5pt, tbl(
  (auto, 1fr, 1fr, 1fr, auto, auto, auto, auto),
  [$t$, с], [$theta(t)$], [$omega(t)$], [$i_a (t)$], [$a_1$], [$a_2$], [$a_3$], [$det Q(t)$],
  ..rows.map(r => (
    fix(r.t, 2), fix(r.center.at(0), 4), fix(r.center.at(1), 4), fix(r.center.at(2), 4),
    sci(r.semi_axes.at(0)), sci(r.semi_axes.at(1)), sci(r.semi_axes.at(2)), sci(r.det),
  )).flatten(),
))
// Проєкції X(t_k) на осі: відрізки [x_i - sqrt(Q_ii), x_i + sqrt(Q_ii)]
#let intervals-table(rows) = tbl(
  (auto, 1fr, 1fr, 1fr),
  [$t$, с], [$theta$, рад], [$omega$, рад/с], [$i_a$, А],
  ..rows.map(r => (
    fix(r.t, 2),
    ..range(3).map(i => $[#fix(r.lo.at(i), 3), #h(0.2em) #fix(r.hi.at(i), 3)]$),
  )).flatten(),
)
#let checks-table(c) = tbl(
  (1fr, auto), align: (left + horizon, center + horizon),
  [*Перевірка*], [*Результат*],
  [(a) $max_t norm(Q(t) - Theta(t) Q_0 Theta^*(t))_F slash norm(Theta Q_0 Theta^*)_F$], [#sci(c.err_Q_max, d: 1)],
  [(b) відносна похибка $det Q(t)$ за формулою Ліувілля @eq-liouville, максимум], [#sci(c.err_det_max, d: 1)],
  [(c) $max_t abs(x(t) - x_"окр"(t))$ (центр проти окремої задачі Коші)], [#sci(c.err_x_max, d: 1)],
  [(d) траєкторії зсередини $M_0$ (#c.n_samples шт.): $max chevron.l Q^(-1) d\, d chevron.r$], [#fix(c.inner_q_max, 6)],
  [(d) траєкторії з межі $M_0$ (#c.n_samples шт.): $max abs(chevron.l Q^(-1) d\, d chevron.r - 1)$], [#sci(calc.max(1 - c.bound_q_min, c.bound_q_max - 1), d: 1)],
)

// ============================ Титул ============================
#page(numbering: none, header: none)[
  #set par(first-line-indent: 0pt, justify: false)
  #align(center)[
    #v(0.6cm)
    #text(16pt)[КИЇВСЬКИЙ НАЦІОНАЛЬНИЙ УНІВЕРСИТЕТ \ ІМЕНІ ТАРАСА ШЕВЧЕНКА]
    #v(2.2cm)
    #text(11.5pt)[Факультет комп'ютерних наук та кібернетики]
    #v(3cm)
    #text(15pt)[ЛАБОРАТОРНА РОБОТА 2]
    #v(0.3cm)
    #text(12pt, weight: "bold")[#subject]
    #v(2cm)
    #text(12pt, weight: "bold")[Динаміка пучка траєкторій моделі сервоприводу: \
      багатозначне відображення та матричне рівняння Ляпунова]
    #v(0.3cm)
    #text(11.5pt)[Варіант 15]
    #v(2.6cm)
    #text(11.5pt)[*Виконав:* студент групи ПМ]
    #v(0.3cm)
    #text(14pt, weight: "bold")[Кіщук Ярослав Ярославович]
    #v(1fr)
    #text(11.5pt)[*Київ* -- 2026]
    #v(1.5cm)
  ]
]

#set page(numbering: "1", header: context [
  #set text(10pt)
  #subject #h(1fr) #lab
  #v(-0.6em)
  #line(length: 100%, stroke: 0.5pt)
])
#counter(page).update(1)

// ============================ Зміст ============================
#show outline.entry.where(level: 1): it => { v(0.9em); strong(it) }
#outline(title: [Зміст], indent: 1.5em)
#pagebreak()

#let P1 = R.params.P1
#let P2 = R.params.P2
#let M1 = R.model.P1
#let M2 = R.model.P2

= Постановка задачі та математична модель

== Модель сервоприводу

Сервопривід складається з двигуна постійного струму з незалежним збудженням
(обмотка збудження $L_f, R_f$ живиться сталою напругою $e_f$, тож магнітне поле стале) і
якоря, на вал якого насаджено вантаж (@fig-scheme). Керування здійснюється напругою
$e_a (t)$, прикладеною до кола якоря. Модель варіанта має вигляд
$
  J (d^2 theta(t)) / (d t^2) + B (d theta(t)) / (d t) = T(t),
$ <eq-mech>
$
  L_a (d i_a (t)) / (d t) + R_a i_a (t) + e_m (t) = e_a (t),
$ <eq-elec>
$
  e_m (t) = K_1 (d theta(t)) / (d t), quad T(t) = K_2 i_a (t).
$ <eq-coupling>
Тут $theta$ -- кут повороту вала, $i_a$ -- струм якоря, $e_m$ -- проти-ЕРС, що наводиться в
обмотці якоря при обертанні, $T$ -- момент двигуна; $R_a$ -- опір обмотки якоря, $L_a$ --
її індуктивність, $B$ -- коефіцієнт в'язкого тертя, $J > 0$ -- момент інерції якоря з
вантажем, $K_1 > 0$ -- стала проти-ЕРС, $K_2 > 0$ -- стала моменту.

#fig("servo_scheme.png", 80%, [Схема сервоприводу (з умови завдання)])<fig-scheme>

Рівняння @eq-mech -- закон обертального руху вала (момент двигуна долає інерцію і в'язке
тертя). Рівняння @eq-elec -- другий закон Кірхгофа для кола якоря: це послідовне
$R L$-коло з джерелом $e_a$ і зустрічною ЕРС $e_m$. Для нерухомого вала ($e_m = 0$) і
сталої напруги це рівно задача про ввімкнення $r L$-кола:

#srcq([[5, §14.4 «Включение $r L$-цепи на постоянное напряжение», с. 238--239]], tr: [«Диференціальне
  рівняння при ввімкненні $r L$-кола (рис. 14.5) на постійну напругу (до джерела ЕРС $E = U$)
  неоднорідне: $r i + L d i slash d t = U$ (14.13), і має розв'язок у вигляді суми усталеної
  та вільної складових $i = i_"у" + i_"в"$. [...] Струм у колі
  $i = i_"у" + i_"в" = U slash r + A e^(-t slash tau)$ (14.14), де $tau = L slash r$.»])[
  «Дифференциальное уравнение при включении $r L$-цепи (рис. 14.5) на постоянное
  напряжение (к источнику ЭДС $E = U$) неоднородное
  $ r i + L d i slash d t = U #h(2em) (14.13) $
  и имеет решение в виде суммы установившейся и свободной составляющих
  $i = i_"у" + i_"св"$. [...] Ток в цепи
  $ i = i_"у" + i_"св" = U slash r + A e^(-t slash tau), #h(2em) (14.14) $
  где $tau = L slash r$.»
]

Отже, струм якоря встановлюється зі сталою часу $tau = L_a slash R_a$ (для набору P1
$tau = 0.25$ с). Співвідношення @eq-coupling описують електромеханічне перетворення
енергії:

#srcq([[6, §9.1, врізка 9.4 «Back EMF», с. 346]], tr: [«Двигун, що обертається, діє як
  генератор і створює напругу $V_b$, яку називають проти-ЕРС; вона протидіє струму, що тече
  в двигун. Проти-ЕРС пропорційна швидкості двигуна: $V_b = K_m omega$, де $K_m$ -- стала
  моменту двигуна, одиниці якої можна також тлумачити як В·с·рад$""^(-1)$.»])[
  «A spinning motor acts like a generator and produces a voltage $V_b$ called the back EMF
  which opposes the current flowing into the motor. Back EMF is proportional to motor speed
  $V_b = K_m omega$, where $K_m$ is the motor torque constant whose units can also be
  interpreted as V s rad$""^(-1)$.»
]

#srcq([[6, §9.7.2, вправа 2, с. 372]], tr: [«Стала моменту двигуна має одиниці
  Н·м·А$""^(-1)$ і дорівнює сталій проти-ЕРС, одиниці якої В·с·рад$""^(-1)$. Покажіть, що
  ці одиниці еквівалентні.»])[
  «The motor torque constant has units of N m A$""^(-1)$ and is equal to the back EMF
  constant which has units of V s rad$""^(-1)$. Show that these units are equivalent.»
]

У позначеннях варіанта $K_1$ -- стала проти-ЕРС, $K_2$ -- стала моменту, тому в одиницях СІ
$K_1 = K_2$; так і беремо в експериментах.

== Зведення до нормальної системи

Зведення виконуємо методом змінних стану:

#srcq([[5, §14.20 «Метод переменных состояния», с. 263--264]], tr: [«Рівняннями стану можна
  назвати будь-яку систему рівнянь, що визначають режим кола. У вужчому сенсі -- це система
  диференціальних рівнянь першого порядку, розв'язана відносно похідних. Методом змінних
  стану назвемо аналіз кола, що ґрунтується на розв'язанні рівнянь стану (першого порядку),
  записаних у формі Коші. [...] як змінні стану доцільно вибирати струми $i_L$ і напруги
  $u_C$. [...] Скорочено диференціальні рівняння стану запишемо в матричній формі так:
  $d/(d t) bold(X)(t) = bold(A) bold(X)(t) + bold(B) bold(F)(t)$ (14.91а).»])[
  «Уравнениями состояния можно назвать любую систему уравнений, определяющих режим цепи.
  В более узком смысле -- это система дифференциальных уравнений первого порядка,
  разрешенная относительно производных. Методом переменных состояния назовем анализ цепи,
  основанный на решении уравнений состояния (первого порядка), записанных в форме Коши.
  [...] в качестве переменных состояния целесообразно выбирать токи $i_L$ и напряжения
  $u_C$. [...] Сокращенно дифференциальные уравнения состояния запишем в матричной форме
  так:
  $ d/(d t) bold(X)(t) = bold(A) bold(X)(t) + bold(B) bold(F)(t) #h(2em) (14.91"а") "»" $
]

Для кола якоря змінна стану -- струм в індуктивності $i_a$; для механічної частини
аналогічну роль відіграють кут і кутова швидкість вала (енергія обертання
$J omega^2 slash 2$). Заміна $x_1 = theta$, $x_2 = dot(theta) = omega$, $x_3 = i_a$ після підстановки
@eq-coupling у @eq-mech, @eq-elec дає
$
  (d x)/(d t) = A x + f(t), quad
  A = mat(0, 1, 0; 0, -B/J, K_2/J; 0, -K_1/L_a, -R_a/L_a), quad
  f(t) = vec(0, 0, e_a (t) slash L_a).
$ <eq-system>

*Спектр матриці $A$.* Перший стовпець $A$ нульовий (кут не входить у праві частини), тому
$
  det(s I - A) = s (s^2 + a_1 s + a_0), quad
  a_1 = B/J + R_a/L_a, quad a_0 = (B R_a + K_1 K_2)/(J L_a).
$ <eq-charpoly>
Отже, $lambda_1 = 0$ з власним вектором $e_1 = (1, 0, 0)^*$, а $lambda_(2,3)$ -- корені
квадратного тричлена з $a_1 > 0$, $a_0 > 0$, тобто $"Re" lambda_(2,3) < 0$. Система
асимптотично стійка за $(omega, i_a)$ і лише нейтрально стійка за $theta$: двигун без
зворотного зв'язку за положенням «не пам'ятає», де він має зупинитися, і похибку кута не
виправляє. При $e_a = "const"$ встановлюються швидкість і струм
$
  omega_infinity = (K_2 e_a)/(B R_a + K_1 K_2), quad
  i_infinity = (B e_a)/(B R_a + K_1 K_2),
$ <eq-steady>
а кут зростає лінійно. Слід матриці
$
  "tr" A = -(B/J + R_a/L_a) < 0
$ <eq-trace>
від'ємний: система дисипативна (тертя і опір розсіюють енергію). Лівий власний вектор для
$lambda_1 = 0$ ($w^* A = 0$, $w_1 = 1$) дорівнює
$
  w = (1, #h(0.3em) (J R_a)/D, #h(0.3em) (K_2 L_a)/D)^*, quad D = B R_a + K_1 K_2,
$ <eq-w>
і при $t -> infinity$ фундаментальна матриця $Theta(t) = e^(A t) -> e_1 w^*$
(решта власних чисел мають від'ємні дійсні частини).

== Параметри моделі

Використано два набори умовних параметрів малого двигуна (@tab-params). Набір P1 дає
дійсні власні числа (аперіодичний перехідний процес), P2 -- менше тертя й більшу сталу
двигуна, власні числа $lambda_(2,3)$ комплексні (коливальний процес).

#let eigs(M) = {
  range(3).map(k => {
    let re = M.eig_re.at(k)
    let im = M.eig_im.at(k)
    if calc.abs(im) < 1e-12 { fix(re, 4) } else { $#fix(re, 4) #if im > 0 [$+$] else [$-$] #fix(calc.abs(im), 4) i$ }
  }).join([; ])
}
#figure(
  tbl((auto, auto, auto, auto, auto, auto, auto, 1fr, auto),
    [], [$J$], [$B$], [$K_1$], [$K_2$], [$R_a$], [$L_a$], [$lambda(A)$], [$"tr" A$],
    [P1], [#P1.J], [#P1.B], [#P1.K1], [#P1.K2], [#P1.Ra], [#P1.La], [#eigs(M1)], [#fix(M1.trace, 1)],
    [P2], [#P2.J], [#P2.B], [#P2.K1], [#P2.K2], [#P2.Ra], [#P2.La], [#eigs(M2)], [#fix(M2.trace, 1)],
  ),
  caption: [Параметри моделі (СІ: кг·м², Н·м·с, В·с/рад, Н·м/А, Ом, Гн) і спектр $A$],
)<tab-params>

Для P1
$
  A = mat(0, 1, 0; 0, #fix(M1.A.at(1).at(1), 1), #fix(M1.A.at(1).at(2), 1); 0, #fix(M1.A.at(2).at(1), 1), #fix(M1.A.at(2).at(2), 1)),
$
коефіцієнт передачі $omega_infinity slash e_a = #fix(M1.speed_gain, 4)$ рад/(В·с),
$w = #vec3(M1.w, 4)$.

== Постановка задачі

Початковий стан відомий неточно: $x(0) in M_0 = cal(E)(x_0, Q_0)$, де
$
  cal(E)(p, Q) = {x in RR^n : chevron.l Q^(-1) (x - p)\, x - p chevron.r <= 1}
$ <eq-ellipsoid>
-- еліпсоїд з центром $p$ і симетричною додатно визначеною матрицею $Q$. Перетином пучка
(ансамблю) траєкторій системи @eq-system у момент $t$ називається множина
$X(t) = union_(x_0 in M_0) x(t, x_0, 0)$.

*Задача.* При заданих $R_a, L_a, B, J, K_1, K_2, e_a (t)$ побудувати багатозначне
відображення $t |-> X(t)$, що описує динаміку пучка траєкторій системи
@eq-mech[]--@eq-coupling, з використанням матричного рівняння Ляпунова; вивести проєкції
графіка багатозначного відображення $"gr" X = {(t, x) : x in X(t)}$, значення
відображення і параметри моделі.

= Опис алгоритму

== Теорема про еліпсоїдальний пучок

Теорему, на якій ґрунтується алгоритм, сформульовано в умові роботи:

#srcq([[1, с. 4]])[
  «Нехай множина початкових станів $M_0 = cal(E)(x_0, Q_0)$, де $x_0 in RR^n$, $Q_0$ --
  $n times n$-матриця, симетрична і додатньовизначена. Тоді пучок траєкторій системи (5)
  в момент $t$
  $ X(t) = cal(E)(x(t), Q(t)), quad t in [t_0, T], #h(2em) (6) $
  де $x(t) = x(t, x_0, t_0)$, $Q(t) = Theta(t, t_0) Q_0 Theta^*(t, t_0)$, $Theta(t, t_0)$ --
  фундаментальна матриця системи $d x slash d t = A(t) x$, нормована за моментом $t_0$.
  Матриця $Q(t)$ може бути знайдена з матричного диференціального рівняння
  $ (d Q)/(d t) = A(t) Q + Q A^*(t), quad Q(t_0) = Q_0, quad t in [t_0, T]. #h(2em) (7) "»" $
]

Те саме твердження є в літературі з еліпсоїдальних методів. Означення еліпсоїда там
збігається з @eq-ellipsoid:

#srcq([[2, §2.1, (2.1), с. 6]])[
  $ cal(E)(q, Q) = {x in RR^n | (x - q)^top Q^(-1) (x - q) <= 1}. #h(2em) (2.1) $
]

#srcq([[2, §2.3.1 «Without Controls or Disturbances», с. 10--11]], tr: [«Для системи без
  керувань і збурень ($B(t) equiv G(t) equiv 0$) динаміка стану набуває вигляду
  $dot(x)(t) = A(t) x(t)$ (2.15), що дає розв'язок $x(t) = Phi(t, t_0) x_0$ (2.16), де
  $Phi(t, t_0)$ -- матриця переходу, що відповідає матриці коефіцієнтів $A(t)$. Тоді множина
  досяжності з еліпсоїдального початкового стану $cal(E)(x_0, X_0)$ сама є еліпсоїдом
  $cal(E)(x_c (t), X(t))$ з центром $x_c (t) = Phi(t, t_0) x_0$ і матрицею форми, яку
  отримують з ОДР $dot(X)(t) = A(t) X(t) + X(t) A^top (t)$ (2.17). Лінійне матричне
  диференціальне рівняння (2.17) добре відоме як диференціальне рівняння Ляпунова і має
  розв'язок $X(t) = Phi(t, t_0) X_0 Phi^top (t, t_0)$ (2.18), тобто матриця форми в будь-який
  момент є конгруентним перетворенням початкової матриці форми [...]. Якщо система
  стаціонарна, тобто $A(t)$ стала в часі, то $Phi(t, t_0) = e^(A(t - t_0))$ і множина
  досяжності має вигляд (2.20).»])[
  «For a system without controls or disturbances ($B(t) equiv G(t) equiv 0$), the state
  dynamics becomes
  $ dot(x)(t) = A(t) x(t), #h(2em) (2.15) $
  which results the solution
  $ x(t) = Phi(t, t_0) x_0, #h(2em) (2.16) $
  where $Phi(t, t_0)$ is the state-transition matrix corresponding to the coefficient matrix
  $A(t)$. Then, the reach set from an ellipsoidal initial state $cal(E)(x_0, X_0)$ is itself
  an ellipsoid $cal(E)(x_c (t), X(t))$ with its center $x_c (t) = Phi(t, t_0) x_0$, and its
  shape matrix obtained from the ODE,
  $ dot(X)(t) = A(t) X(t) + X(t) A^top (t). #h(2em) (2.17) $
  The linear matrix differential equation (2.17) is well-known as the Lyapunov differential
  equation, and admits solution
  $ X(t) = Phi(t, t_0) X_0 Phi^top (t, t_0), #h(2em) (2.18) $
  that is, the shape matrix at any time is the congruence transformation of the initial
  shape matrix [...]. If the system is time-invariant, i.e., $A(t)$ is constant in time,
  then $Phi(t, t_0) = e^(A(t - t_0))$ and the reach set is
  $ cal(X)[t] = cal(E)(e^(A(t - t_0)) x_0, #h(0.3em) e^(A(t - t_0)) X_0 e^(A^top (t - t_0))). #h(2em) (2.20) "»" $
]

У нас є відомий вхід $f(t)$, який зсуває центр. Цей випадок у [2] -- частковий випадок
системи з керуванням $dot(x) = A x + B u$, $u(t) in cal(E)(u_c (t), U(t))$:

#srcq([[2, §2.3.2, (2.22)--(2.23), с. 12]], tr: [«Рівність (2.21) можна еквівалентно
  записати як (2.22) з вектором центру, що визначається рівнянням (2.10): (2.23).»])[
  «Eqn. (2.21) can be equivalently described as
  $ cal(X)(t, t_0, cal(X)_0) = x_c (t) plus.dot Phi(t, t_0) cal(E)(0, X_0) plus.dot
    integral_(t_0)^t Phi(t, tau) cal(E)(0, B(tau) U(tau) B^top (tau)) d tau #h(2em) (2.22) $
  with the center vector guided by the Eqn. (2.10),
  $ x_c (t) = Phi(t, t_0) x_0 + integral_(t_0)^t Phi(t, tau) B(tau) u_c (tau) d tau. #h(2em) (2.23) "»" $
]

Для системи @eq-system вхід відомий точно: $B = I$, $u_c (t) = f(t)$, $U(t) = 0$, тому
кожна множина $cal(E)(0, B U B^top) = {0}$, інтеграл у (2.22) зникає, а $x_c (t)$ з (2.23) --
це розв'язок системи з $x(t_0) = x_0$ (формула Коші). Звідси й з (2.20) маємо:
$
  X(t) = cal(E)(x(t), Q(t)), quad Q(t) = Theta(t, t_0) Q_0 Theta^*(t, t_0),
$ <eq-bundle>
де $x(t)$ -- розв'язок системи з $x(t_0) = x_0$, $Theta(t, t_0)$ -- нормована при $t_0$
фундаментальна матриця системи $dot(x) = A(t) x$. Матриця $Q(t)$ є розв'язком матричного
диференціального рівняння Ляпунова
$
  (d Q)/(d t) = A(t) Q + Q A^*(t), quad Q(t_0) = Q_0.
$ <eq-lyap>
Для сталої $A$ маємо $Theta(t, 0) = e^(A t)$, тож $Q(t) = e^(A t) Q_0 e^(A^* t)$.

Той самий результат дають леми з [3], де $X(t, s)$ -- матриця переходу, а керування
обмежене еліпсоїдом $u(t) in cal(E)(q(t), Q(t))$:

#srcq([[3, (3), леми 1.2--1.3, с. 2--3]], tr: [«(3) [...] Її опорна функція ([13]) дорівнює
  $rho(l | cal(E)) = max{(l, x) | x in cal(E)} = (l, q(t)) + (l, Q(t) l)^(1 slash 2)$. [...]
  *Лема 1.2.* Має місце рівність (5), де $x^star (t) = dots$ [...] *Лема 1.3.* Опорна
  функція множини досяжності дорівнює (6).»])[
  $ "«" cal(E)(q(t), Q(t)) = {u : (u - q(t), Q^(-1)(t)(u - q(t))) <= 1}, #h(2em) (3) $
  [...] Its support function ([13]) is
  $ rho(l | cal(E)(q(t), Q(t))) = max{(l, x) | x in cal(E)(q(t), Q(t))} = (l, q(t)) + (l, Q(t) l)^(1 slash 2). $
  [...] *Lemma 1.2* The following relation holds:
  $ cal(X)(t, t_0, cal(E)(x_0, X_0)) = x^star (t) + X(t, t_0) cal(E)(0, X_0) +
    integral_(t_0)^t X(t, s) cal(E)(0, B(s) Q(s) B'(s)) d s, #h(2em) (5) $
  where $x^star (t) = X(t, t_0) x_0 + integral_(t_0)^t X(t, s) B(s) q(s) d s$.
  [...] *Lemma 1.3* The support function
  $ rho(l | cal(X)(t, t_0, cal(E)(x_0, X_0))) & = (l, x^star (t)) + (l, X(t, t_0) X_0 X'(t, t_0) l)^(1 slash 2) \
    & + integral_(t_0)^t (l, X(t, s) B(s) Q(s) B'(s) X'(t, s) l)^(1 slash 2) d s. #h(2em) (6)"»" $
]

При $Q(s) = 0$ (вхід відомий) інтеграли в (5), (6) зникають, і (6) збігається з опорною
функцією еліпсоїда $cal(E)(x^star (t), X(t, t_0) X_0 X'(t, t_0))$, тобто з @eq-bundle.
Ширший контекст -- еліпсоїдальні методи для систем з невідомими обмеженими збуреннями:

#srcq([[4, Foreword]], tr: [«Це друга зі серії статей з раннім викладом застосування
  еліпсоїдальних методів до задач моделювання динамічних систем. Стаття присвячена задачі
  синтезу керування для лінійної системи з невідомими, але обмеженими збуреннями, яка
  зводиться до синтезованого нелінійного диференціального включення.»])[
  «This is the second of a series of papers giving an early account of the application of
  ellipsoidal techniques to problems of modeling dynamical systems. The paper deals with
  the problem of control synthesis for a linear system with unknown but bounded disturbances
  which ends up in a synthesized nonlinear differential inclusion.»
]

Наслідки, які використано далі:
+ матриця $Q(t)$ *не залежить від* $f$, тобто від напруги $e_a (t)$: керування лише зсуває
  центр пучка, а форма і розміри $X(t)$ однакові для будь-якого $e_a$;
+ еліпсоїд не може виродитися за скінченний час ($Theta$ невироджена), але при
  $t -> infinity$ з $Theta(t) -> e_1 w^*$ випливає $Q(t) -> chevron.l Q_0 w\, w chevron.r e_1 e_1^*$:
  пучок стискається у відрізок уздовж осі $theta$ довжини $2 sqrt(chevron.l Q_0 w\, w chevron.r)$,
  а при $e_a = 0$ центр прямує до $(chevron.l w\, x_0 chevron.r, 0, 0)$ -- кута, на якому
  зупиниться вал.

== Об'єм пучка: формула Ліувілля

Об'єм еліпсоїда $cal(E)(p, Q) subset RR^3$ дорівнює $4/3 pi sqrt(det Q)$. З @eq-bundle
$det Q(t) = det Q_0 (det e^(A t))^2$, а $det e^(A t) = product_k e^(lambda_k t) = e^(t "tr" A)$,
тому
$
  det Q(t) = det Q_0 dot e^(2 t "tr" A), quad
  "vol" X(t) = "vol" M_0 dot e^(t "tr" A).
$ <eq-liouville>
Для сервоприводу $"tr" A < 0$ @eq-trace, і об'єм пучка експоненційно спадає: на відміну
від консервативних механічних систем (де за теоремою Ліувілля фазовий об'єм зберігається),
тертя й опір обмотки «стискають» множину можливих станів. Формула @eq-liouville не
використовується в обчисленнях і слугує незалежною перевіркою розв'язку @eq-lyap.

== Опорна функція і межа проєкцій

Опорна функція еліпсоїда (див. цитату з [3] у розділі 2.1)
$
  c(cal(E)(p, Q), psi) = max_(x in cal(E)(p, Q)) chevron.l x\, psi chevron.r
    = chevron.l p\, psi chevron.r + sqrt(chevron.l Q psi\, psi chevron.r).
$ <eq-support>
Максимум досягається в точці дотику опорної гіперплощини з нормаллю $psi$, яка дорівнює
градієнту опорної функції за $psi$:
$
  x(psi) = p + (Q psi) / sqrt(chevron.l Q psi\, psi chevron.r).
$ <eq-boundary>
Множина $X(t) subset RR^3$, а графік $"gr" X subset RR^4$, тому їх зображуємо через
ортогональні проєкції.

- *Проєкція на вісь $x_i$* (напрямки $psi = plus.minus e_i$): відрізок
  $[x_i (t) - sqrt(Q_(i i)(t)), #h(0.2em) x_i (t) + sqrt(Q_(i i)(t))]$. Проєкція графіка на
  площину $(t, x_i)$ -- смуга між цими межами.
- *Проєкція на площину $(x_i, x_j)$*: беремо $psi$ з нульовими координатами поза $i, j$;
  проєкції точок @eq-boundary заповнюють межу еліпса $cal(E)(P p, P Q P^*)$, $P$ --
  оператор проєкції (лінійний образ еліпсоїда -- еліпсоїд). Щоб точки межі лягали
  рівномірно і для дуже витягнутих еліпсів, напрямки беремо у вигляді
  $psi = M^(-1) L u$, $u = (cos phi, sin phi)$, де $M = P Q P^*$, $M = L L^*$ (розклад
  Холецького). Тоді $chevron.l M psi\, psi chevron.r = 1$ і проєкція @eq-boundary дорівнює
  $P p + L u$.
- *Проєкція графіка на $(t, x_i, x_j)$* -- «труба», складена з еліптичних перерізів.
- Оскільки $n = 3$, еліпсоїди $X(t)$ можна зобразити і цілком: $x(t) + Q^(1/2)(t) u$,
  $norm(u) = 1$.

== Чисельна схема

Невідомі $x(t) in RR^3$ і $Q(t) in RR^(3 times 3)$ об'єднуємо у вектор
$z = (x, "vec" Q) in RR^12$ і розв'язуємо задачу Коші
$
  dot(x) = A x + f(t), quad dot(Q) = A Q + Q A^*, quad x(0) = x_0, quad Q(0) = Q_0,
$
явним методом Рунге--Кутти порядку 8 з автоматичним вибором кроку (DOP853 у
`scipy.integrate.solve_ivp` [7]), відносна і абсолютна точності
$#sci(R.rtol, d: 0)$ і $#sci(R.atol, d: 0)$. Розв'язок обчислюється на сітці з 601 вузла
на $[0, T]$ (плюс моменти, у які виводяться таблиці). Через похибки округлення $Q$ втрачає
симетричність на рівні $10^(-16)$, тому після інтегрування беремо $(Q + Q^*) slash 2$.
Множину значень $X(t)$ відновлюємо за $x(t), Q(t)$: півосі -- корені власних чисел $Q(t)$,
межі проєкцій -- за @eq-boundary.

#srcq([[7]], tr: [«Розв'язує задачу Коші для системи ЗДР. [...] 'DOP853': явний метод
  Рунге--Кутти порядку 8. Реалізація на Python алгоритму "DOP853", спочатку написаного на
  Fortran. [...] rtol, atol: відносна й абсолютна точності. Розв'язувач підтримує оцінки
  локальної похибки меншими за `atol + rtol * abs(y)`.»])[
  «Solve an initial value problem for a system of ODEs. [...] 'DOP853': Explicit
  Runge-Kutta method of order 8 [13]. Python implementation of the "DOP853" algorithm
  originally written in Fortran [14]. [...] rtol, atol: Relative and absolute tolerances.
  The solver keeps the local error estimates less than `atol + rtol * abs(y)`.»
]

== Перевірка правильності

+ *(a)* $Q(t)$ з @eq-lyap порівнюється з явною формулою $e^(A t) Q_0 e^(A^* t)$; матричну
  експоненту обчислює `scipy.linalg.expm`:
  #srcq([[8]], tr: [«Обчислює матричну експоненту масиву. [...] Реалізує алгоритм з [1],
    що по суті є апроксимацією Паде змінного порядку [...]»])[
    «Compute the matrix exponential of an array. [...] Implements the algorithm given in [1],
    which is essentially a Pade approximation with a variable order [...]»
  ]
+ *(b)* $det Q(t)$ порівнюється з формулою Ліувілля @eq-liouville.
+ *(c)* центр $x(t)$ порівнюється з окремо розв'язаною задачею Коші для $x$.
+ *(d)* Метод Монте-Карло: 300 точок, рівномірно розподілених у $M_0$, і 300 точок на межі
  $M_0$ (вигляду $x_0 + Q_0^(1/2) u$, $norm(u) = 1$) інтегруються окремо. Для кожної
  обчислюється $chevron.l Q^(-1)(t) d\, d chevron.r$, $d = x - x(t)$: для внутрішніх точок ця
  величина має бути $<= 1$, для граничних -- дорівнювати $1$ (лінійне відображення
  переводить межу в межу).
+ *(e)* При $e_a = 0$ значення при великих $t$ порівнюються з граничним станом
  $theta_infinity = chevron.l w\, x_0 chevron.r$, $sqrt(Q_(11)(infinity)) = sqrt(chevron.l Q_0 w\, w chevron.r)$.

*Обумовленість.* Півосі $X(t)$ зменшуються з різною швидкістю ($e^(lambda_k t)$), тож число
обумовленості $"cond" Q(t)$ росте приблизно як $e^(2 (lambda_1 - "Re" lambda_3) t)$. Абсолютна
похибка елементів $Q$ при цьому лишається на рівні $10^(-16) norm(Q)$, а відносна похибка
найменшого власного числа (і $det Q$) зростає приблизно пропорційно $"cond" Q$. Тому горизонт
моделювання обрано так, щоб $"cond" Q(T) lt.tilde 10^(14)$: на довших інтервалах пучок
стає числово виродженим (практично відрізком).

== Алгоритм

+ За параметрами $R_a, L_a, B, J, K_1, K_2$ побудувати $A$ і $f(t)$ @eq-system; обчислити
  спектр $A$, $"tr" A$, $w$.
+ Задати $x_0$, $Q_0$ (симетрична, додатно визначена), $T$ і сітку моментів.
+ Розв'язати задачу Коші для $(x, Q)$ методом Рунге--Кутти; симетризувати $Q$.
+ Для моментів $t_k$ вивести значення відображення: центр, $Q(t_k)$, півосі, $det Q$,
  проєкції на осі.
+ Побудувати проєкції графіка (смуги, перерізи, «трубу», еліпсоїди) за @eq-boundary.
+ Виконати перевірки (a)--(e).

= Опис програми

Програму написано мовою Python 3 (NumPy, SciPy, Matplotlib) у вигляді ноутбука
`lab2.ipynb`: кожен крок алгоритму -- окрема комірка з поясненням і формулами, експерименти
виконуються послідовно з виводом таблиць і рисунків. Запуск -- «Run All» у Jupyter або
`jupyter nbconvert --to notebook --execute lab2.ipynb`. Основні функції наведено в
@tab-funcs; текст обчислювальної частини -- у додатку А.

#figure(
  {
  show raw: set text(size: 7.8pt)
  tbl((40%, 1fr), align: left + horizon,
    [*Функція*], [*Призначення*],
    [`build_A(p)`, `build_f(p, ea)`], [матриця $A$ і вектор $f(t)$ системи @eq-system],
    [`model_summary(p)`], [спектр $A$, $"tr" A$, коефіцієнти @eq-charpoly, @eq-steady, вектор $w$ @eq-w],
    [`bundle_rhs`, `solve_bundle`], [права частина системи для $(x, "vec" Q)$ і її інтегрування (DOP853)],
    [`ellipsoid_info`, `value_table`], [значення відображення $X(t_k)$: центр, $Q$, півосі, $det Q$, проєкції на осі],
    [`support`, `boundary_point`, `boundary_2d`], [опорна функція @eq-support, точка дотику @eq-boundary, межа проєкції на площину],
    [`ellipsoid_surface`], [поверхня тривимірного еліпсоїда],
    [`sample_ellipsoid`, `simulate_samples`, `checks`], [вибіркові траєкторії і перевірки (a)--(d)],
    [`plot_*`, `draw_shaft`, `make_shaft_animation`], [рисунки звіту, кадри вала, анімація GIF/MP4],
    [`run`, `main()`], [експерименти, вивід таблиць, збереження `results.json` і рисунків],
  )},
  caption: [Основні функції програми],
)<tab-funcs>

Числові результати записуються у `report/figures/results.json`, звідки їх читає цей звіт,
тож таблиці відповідають фактичному запуску програми. Анімація руху вала з множиною
можливих станів зберігається у файлах `e3_shaft_anim.mp4` / `e3_shaft_anim.gif`.

= Обчислювальні експерименти

Позначення в таблицях: $a_1 >= a_2 >= a_3$ -- півосі еліпсоїда $X(t)$ (корені власних
чисел $Q(t)$); $theta$ -- у радіанах, $omega$ -- у рад/с, $i_a$ -- в амперах, $e_a$ -- у вольтах.

== Експеримент 1. Вільний вибіг вала

#let e1 = R.e1
Напруга не подається ($e_a = 0$, параметри P1). Вал обертається зі швидкістю, відомою
наближено: $x_0 = #vec3(e1.x0, 1)$, $Q_0 = #fix(calc.sqrt(e1.Q0.at(0).at(0)), 1)^2 I$
(куля радіуса $0.3$), $T = #e1.T$ с. Значення відображення наведено в @tab-e1, перевірки --
в @tab-e1-chk.

#figure(values-table(e1.rows), caption: [Е1: значення відображення $X(t) = cal(E)(x(t), Q(t))$])<tab-e1>
#figure(intervals-table(e1.rows), caption: [Е1: проєкції $X(t)$ на осі координат])<tab-e1-int>
#figure(checks-table(e1.checks), caption: [Е1: перевірки правильності])<tab-e1-chk>

#fig("e1_bands.png", 86%, [Е1: проєкції графіка $"gr" X$ на площини $(t, x_i)$ і вибіркові траєкторії])<fig-e1-bands>
#fig("e1_sections.png", 100%, [Е1: перерізи $X(t_k)$ у проєкціях на координатні площини; точки -- положення 300 вибіркових траєкторій у ті самі моменти])<fig-e1-sec>
#fig("e1_ellipsoids3d.png", 70%, [Е1: еліпсоїди $X(t_k)$ у просторі $(theta, omega, i_a)$; чорні точки -- траєкторії з межі $M_0$])<fig-e1-3d>
#fig("e1_tube.png", 70%, [Е1: проєкція графіка на $(t, theta, omega)$])<fig-e1-tube>

Швидкість і струм загасають, і невизначеність за ними зменшується: півось за $i_a$
зменшилась з $0.3$ до $#sci(e1.rows.last().semi_axes.at(2))$ (стала часу кола якоря мала), за
$omega$ -- до $#sci(e1.rows.last().semi_axes.at(1))$. Натомість невизначеність кута
*зростає*: з $0.3$ до $#fix(e1.rows.last().semi_axes.at(0), 3)$ рад, бо до початкової похибки
кута додається проінтегрована невизначеність швидкості. Еліпсоїд витягується вздовж осі
$theta$ і сплющується (@fig-e1-sec, @fig-e1-3d), $det Q$ спадає на 13 порядків. Граничний
стан (перевірка (e)): вал зупиниться на куті $theta_infinity = chevron.l w\, x_0 chevron.r =
#fix(e1.limit.theta_inf, 4)$ (при $t = T$: $#fix(e1.limit.theta_T, 4)$), гранична піввісь
$sqrt(chevron.l Q_0 w\, w chevron.r) = #fix(e1.limit.half_inf, 4)$ (при $t = T$:
$#fix(e1.limit.half_T, 4)$). Усі вибіркові траєкторії лишаються в $X(t)$, а траєкторії з
межі $M_0$ -- на межі $X(t)$ з точністю $10^(-6)$ (@tab-e1-chk).

== Експеримент 2. Сталий вхід

#let e2 = R.e2
Ті самі $Q_0$ і параметри, але вал стартує зі стану спокою $x_0 = 0$ і подається стала
напруга $e_a = #e2.ea$ В (@tab-e2, @fig-e2-bands).

#figure(values-table(e2.rows), caption: [Е2: значення відображення, $e_a = #e2.ea$ В])<tab-e2>
#fig("e2_bands.png", 86%, [Е2: проєкції графіка $"gr" X$, $e_a = #e2.ea$ В])<fig-e2-bands>
#fig("e2_sections.png", 80%, [Е2: перерізи $X(t_k)$])<fig-e2-sec>

Центр виходить на режим @eq-steady: $omega_infinity = #fix(e2.w_inf, 4)$ рад/с,
$i_infinity = #fix(e2.i_inf, 4)$ А (при $t = T$: $omega = #fix(e2.rows.last().center.at(1), 4)$,
$i_a = #fix(e2.rows.last().center.at(2), 4)$), кут зростає лінійно. Стовпці півосей і
$det Q$ в @tab-e2 і @tab-e1 збігаються: $max_t abs(Q_"Е1"(t) - Q_"Е2"(t)) =
#sci(e2.dQ_e1_e2, d: 1)$, що чисельно підтверджує наслідок 1 теореми -- напруга зсуває пучок,
не змінюючи його форми. Перевірки: (a) $#sci(e2.checks.err_Q_max, d: 1)$, (b)
$#sci(e2.checks.err_det_max, d: 1)$, (d) межа $in [#fix(e2.checks.bound_q_min, 5),
#fix(e2.checks.bound_q_max, 5)]$ (точність трохи нижча, бо $theta$ сягає 25 рад, а абсолютна
похибка траєкторій пропорційна їх величині).

== Експеримент 3. Знакозмінна напруга і недіагональна $Q_0$

#let e3 = R.e3
Сервопривід «гойдають» реверсивною напругою $e_a (t) = #e3.amp sin(2 pi t)$ (частота
$#e3.freq$ Гц), $x_0 = 0$, $T = #e3.T$ с. Початкова невизначеність задана
середньоквадратичними піввісями проєкцій $sqrt(Q_(0, i i)) = (#e3.std.at(0), #e3.std.at(1), #e3.std.at(2))$
і коефіцієнтом кореляції $0.6$ між $omega$ і $i_a$: $Q_0 = D C D$, $D = "diag"(sqrt(Q_(0,i i)))$.
Фізичний зміст: кут вала вимірюється енкодером точно, а швидкість і струм відомі гірше
і взаємопов'язані (струм пропорційний моменту, що розганяє вал).

#figure(values-table(e3.rows), caption: [Е3: значення відображення, $e_a = #e3.amp sin 2 pi t$])<tab-e3>
#figure(intervals-table(e3.rows), caption: [Е3: проєкції $X(t)$ на осі -- можливі кут, швидкість і струм])<tab-e3-int>
#fig("e3_bands.png", 86%, [Е3: проєкції графіка $"gr" X$ на площини $(t, x_i)$])<fig-e3-bands>
#fig("e3_sections.png", 80%, [Е3: перерізи $X(t_k)$])<fig-e3-sec>
#fig("e3_tube.png", 66%, [Е3: проєкція графіка на $(t, theta, omega)$])<fig-e3-tube>
#fig("e3_shaft.png", 100%, [Е3: стан вала у моменти $t_k$. Сектор -- множина можливих кутів (проєкція $X(t_k)$ на вісь $theta$), стрілка -- кут центру; під валом -- відрізки можливих $omega$ та $i_a$ на шкалах $[-max, max]$])<fig-e3-shaft>

Центр пучка коливається з частотою напруги, проходячи вперед-назад (@fig-e3-bands).
Хоча кут на початку відомий з точністю $plus.minus #e3.std.at(0)$ рад, вже через
$1$ с множина можливих кутів має ширину $#fix(e3.rows.at(4).hi.at(0) - e3.rows.at(4).lo.at(0), 2)$ рад,
а при $t = #e3.T$ с -- $#fix(e3.rows.last().hi.at(0) - e3.rows.last().lo.at(0), 2)$ рад
(@fig-e3-shaft, @tab-e3-int): початкова невизначеність швидкості переходить у
невизначеність кута і далі не зменшується. Це
наочний прояв нульового власного числа: без зворотного зв'язку за кутом розімкнений
сервопривід не може «забути» початкову похибку швидкості. Півширина множини можливих струмів зменшується з $#e3.std.at(2)$ до
$#fix((e3.rows.at(4).hi.at(2) - e3.rows.at(4).lo.at(2)) / 2, 3)$ А вже за $1$ с, швидкостей --
з $#e3.std.at(1)$ до $#fix((e3.rows.last().hi.at(1) - e3.rows.last().lo.at(1)) / 2, 3)$ рад/с за $#e3.T$ с. Перевірки (@tab-e3-chk) підтверджують
правильність при $"cond" Q(T) = #sci(e3.checks.cond_T, d: 1)$.

#figure(checks-table(e3.checks), caption: [Е3: перевірки правильності])<tab-e3-chk>

== Експеримент 4. Вплив параметрів двигуна

#let e4 = R.e4
Вільний вибіг з $x_0 = #vec3(e4.x0, 1)$, $Q_0 = 0.3^2 I$, $T = #e4.T$ с для наборів P1
(дійсні власні числа) і P2 (комплексні, @tab-params). Перерізи в площині $(omega, i_a)$
наведено на @fig-e4, значення -- в @tab-e4.

#fig("e4_compare.png", 100%, [Е4: перерізи $X(t_k)$ у площині $(omega, i_a)$ для P1 і P2])<fig-e4>

#figure(
  tbl((auto, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    table.cell(rowspan: 2)[$t$, с], table.cell(colspan: 3)[P1], table.cell(colspan: 3)[P2],
    [$omega(t)$], [$a_1$], [$det Q$], [$omega(t)$], [$a_1$], [$det Q$],
    ..range(e4.P1.rows.len()).map(k => {
      let a = e4.P1.rows.at(k)
      let b = e4.P2.rows.at(k)
      (fix(a.t, 1), fix(a.center.at(1), 4), fix(a.semi_axes.at(0), 4), sci(a.det),
       fix(b.center.at(1), 4), fix(b.semi_axes.at(0), 4), sci(b.det))
    }).flatten(),
  ),
  caption: [Е4: вільний вибіг для наборів P1 і P2],
)<tab-e4>

Для P2 центр у площині $(omega, i_a)$ описує загасаючу спіраль (швидкість змінює знак:
вал «перебігає» і повертається), а еліпс-переріз обертається разом з потоком; для P1 рух
монотонний. Слід $"tr" A$ для P2 майже вдвічі менший за модулем ($#fix(M2.trace, 1)$ проти
$#fix(M1.trace, 1)$), тому об'єм пучка спадає повільніше (@fig-det), але гранична
невизначеність кута більша: $sqrt(chevron.l Q_0 w\, w chevron.r) = #fix(e4.P2.limit.half_inf, 3)$
проти $#fix(e4.P1.limit.half_inf, 3)$ рад, бо при слабкому терті двигун довше «пам'ятає»
невідому початкову швидкість (компонента $w_2 = J R_a slash D$ більша).

#fig("det_liouville.png", 100%, [Зліва: $det Q(t)$ з рівняння Ляпунова (кольорові лінії) і за формулою Ліувілля @eq-liouville (пунктир). Справа: відносна похибка $det Q$ і $10^(-16) dot "cond" Q(t)$])<fig-det>

На @fig-det (зліва) обчислені $det Q(t)$ лежать на прямих з нахилом $2 "tr" A$ у
логарифмічному масштабі. Справа видно, що відносна похибка $det Q$ росте разом з
обумовленістю $Q(t)$ і обмежена величиною порядку $10^(-16) "cond" Q$ -- це втрата
відносної точності найменшої півосі при сплющенні еліпсоїда, а не похибка методу: похибка
самої матриці (перевірка (a)) у всіх експериментах не перевищує
$#sci(calc.max(e1.checks.err_Q_max, e3.checks.err_Q_max, e4.P2.checks.err_Q_max), d: 1)$.

= Висновки

+ Модель сервоприводу @eq-mech[]--@eq-coupling зведено до лінійної системи @eq-system з
  матрицею $A$, що має власне число $lambda_1 = 0$ (кут не стабілізується) і два власні
  числа з від'ємними дійсними частинами; $"tr" A = -(B slash J + R_a slash L_a) < 0$.
+ На основі теореми про еліпсоїдальний пучок [2, 3] побудовано багатозначне відображення
  $X(t) = cal(E)(x(t), Q(t))$; матриця $Q(t)$ знаходиться з матричного рівняння Ляпунова
  @eq-lyap, яке інтегрується разом із системою для центру (12 рівнянь, метод Рунге--Кутти
  8-го порядку). Межі проєкцій будуються через опорну функцію еліпсоїда.
+ Правильність підтверджено п'ятьма незалежними способами: збіг із
  $e^(A t) Q_0 e^(A^* t)$ до $10^(-12)$, формула Ліувілля, окремий розв'язок для центру,
  300 + 300 вибіркових траєкторій (внутрішні лишаються всередині, граничні -- на межі з
  точністю $10^(-5)$..$10^(-10)$) і аналітичний граничний стан $Q(infinity) = chevron.l Q_0 w\, w chevron.r e_1 e_1^*$.
+ Об'єм пучка спадає як $e^(t "tr" A)$ (система дисипативна), але не рівномірно: множина
  можливих швидкостей і струмів стискається, а множина можливих кутів *зростає* і прямує до
  відрізка довжини $2 sqrt(chevron.l Q_0 w\, w chevron.r)$. Тобто без зворотного зв'язку за
  положенням неточність початкового стану неминуче переходить у неточність кута.
+ Форма пучка не залежить від напруги керування $e_a (t)$ -- вона лише зсуває центр (Е2
  збігається з Е1 до $10^(-14)$). При комплексних власних числах (менше тертя) центр рухається
  по спіралі, переріз обертається, об'єм спадає повільніше, а гранична невизначеність кута
  більша.
+ Через різні швидкості загасання півосей $"cond" Q(t)$ росте експоненційно, що обмежує
  відносну точність найменшої півосі; на великих горизонтах пучок практично вироджується
  у відрізок.

= Список використаних джерел

#set par(first-line-indent: 0pt)
Джерела 1--6 містяться в папці `literature/` проєкту, 7--8 -- документація за посиланням.

+ Лабораторна робота 2 з курсу «Проблеми багатозначного аналізу», варіант 15: методичні вказівки. -- К.: КНУ імені Тараса Шевченка, 2026. -- 5 с.
+ Gianfortone L. Ellipsoidal Algorithm for Fast Computation of Reachable Tubes: M.S.
  thesis. -- University of California, Santa Cruz, 2018. -- URL:
  #link("https://escholarship.org/uc/item/67p1s5fv")
+ Kurzhanski A.B., Varaiya P. Ellipsoidal techniques for reachability analysis: internal
  approximation \/\/ Systems & Control Letters. -- 2000. -- Vol. 41. -- P. 201--211.
+ Kurzhanski A.B., Vályi I. Ellipsoidal Techniques: Control Synthesis for Uncertain
  Systems. -- Laxenburg: IIASA, 1991. -- Working Paper WP-91-007.
+ Зевеке Г.В., Ионкин П.А., Нетушил А.В., Страхов С.В. Основы теории цепей. -- 5-е изд.
  -- М.: Энергоатомиздат, 1989. -- 528 с.
+ Corke P. Robotics, Vision and Control: Fundamental Algorithms in Python. -- 3rd ed. --
  Cham: Springer, 2023.
+ SciPy: `scipy.integrate.solve_ivp` -- documentation. -- URL:
  #link("https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html")
+ SciPy: `scipy.linalg.expm` -- documentation. -- URL:
  #link("https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.expm.html")

// ============================ Додаток ============================
#counter(heading).update(0)
#set heading(numbering: "А.1")
#pagebreak(weak: true)

= Текст програми

Обчислювальна частина ноутбука `lab2.ipynb` -- комірки з позначкою `report` (розділи 1--5:
модель, рівняння Ляпунова, значення відображення, геометрія еліпсоїда, перевірки); комірки
з рисунками та експериментами опущено.

#let nb = json("../lab2.ipynb")
#let cell-src(c) = if type(c.source) == str { c.source } else { c.source.join("") }
#let src = (nb.cells
  .filter(c => c.cell_type == "code" and "report" in c.metadata.at("tags", default: ()))
  .map(cell-src)
  .join("\n\n"))
#raw(src, lang: "python", block: true)
