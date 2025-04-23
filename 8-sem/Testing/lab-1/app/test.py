import pytest
import SegmentLine, SlopeInterceptLine, LineClassifier
from app import LinesApp
from utils import InvalidLineException

###############################################################################
# Тести для допустимих класів ситуацій (коректні дані)
###############################################################################

#  Прямі не перетинаються (усі три паралельні, але не співпадають (можуть співпасти тільки дві))
@pytest.mark.parametrize("a1,b1,a2,b2,k3,b3", [
    (-126, -126, -125, -125, -1, -125),
    (-120, -120, -118, -118, -1, -119),
    (10, -10, 20, -20, 1, 15),
    (126, 126, 125, 125, -1, 125),
    (120, 120, 118, 118, -1, 119),
    (120, -120, 18, -18, 1, 119)
])
def test_parallel(a1, b1, a2, b2, k3, b3):
    """
    Якщо всі три прямі паралельні (але не співпадають), має повернутися:
      "Прямі не перетинаються"
    """
    line1 = SegmentLine.SegmentLine(a1, b1)
    line2 = SegmentLine.SegmentLine(a2, b2)
    line3 = SlopeInterceptLine.SlopeInterceptLine(k3, b3)
    classifier = LineClassifier.LineClassifier(line1, line2, line3)
    result = classifier.classify()
    print(result)
    assert result == "Прямі не перетинаються"


# Прямі перетинаються в одній точці (конкурентні прямі)
@pytest.mark.parametrize("a1, b1, a2, b2, k3, b3, common_point", [
    # Test 1 (Граничний нижній): використання значень, близьких до -126
    (-126, 10, -125, 10, -126, 10, (0, 10)),
    # Test 2 (Граничний верхній): використання значень, близьких до 126
    (126, 10, 125, 10, 126, 10, (0, 10)),
    # Test 3 (Типові значення): середній діапазон
    (20, 10, 30, 10, 1, 10, (0, 10)),
    # Test 4 (Комбінація граничного і середнього): перша з граничних, друга з типових
    (-126, 10, 30, 10, 0, 10, (0, 10)),
])
def test_concurrent(a1, b1, a2, b2, k3, b3, common_point):
    """
    Тест для конкурентних прямих – всі три перетинаються в одній точці.
    Очікуване: рядок результату містить фразу "Прямі перетинаються в одній точці"
    і має містити координати спільної точки, наприклад, "(0.000000, 10.000000)".
    """
    line1 = SegmentLine.SegmentLine(a1, b1)
    line2 = SegmentLine.SegmentLine(a2, b2)
    line3 = SlopeInterceptLine.SlopeInterceptLine(k3, b3)
    classifier = LineClassifier.LineClassifier(line1, line2, line3)
    result = classifier.classify()

    print(result)

    # Очікуємо, що рядок містить ключову фразу для конкурентних прямих:
    expected_str = "Прямі перетинаються в одній точці"
    assert expected_str in result, f"Результат '{result}' не містить '{expected_str}'"

    # Перевіряємо, що спільна точка співпадає з очікуваною (за форматуванням до 6 знаків після коми)
    common_str = f"({common_point[0]:.6f}, {common_point[1]:.6f})"
    assert common_str in result, f"Спільна точка '{common_str}' не знайдена в результаті '{result}'"


# Прямі перетинаються в двох точках
@pytest.mark.parametrize("a1,b1,a2,b2,k3,b3,expected", [
    # Test 1: Граничний випадок з великими від'ємними значеннями
    (-126, -126, -125, -125, 0, 50, ((-176.000000, 50.000000), (-175.000000, 50.000000))),
    # Test 2: Типовий випадок з позитивними значеннями
    (100, 100, 90, 90, 1, 10, ((45.000000, 55.000000), (40.000000, 50.000000))),
    # Test 3: Типовий випадок з малими значеннями
    (3, 4, 6, 8, 2, 5, ((-0.300000, 4.400000), (0.900000, 6.800000))),
    # Test 4: Спеціальний випадок – комбінація негативних і позитивних параметрів
    (-50, 20, -40, 16, 0.5, -20, ((400.000000, 180.000000), (360.000000, 160.000000))),
    # Test 5: Граничний випадок із використанням максимальних значень
    (126, -126, 120, -120, 0, -10, ((116.000000, -10.000000), (110.000000, -10.000000))),
    # Test 6: Спеціальний випадок із змішанням малих від'ємних значень
    (-10, 50, -8, 40, 2, -20, ((-23.333333, -66.666667), (-20.000000, -60.000000))),
])
def test_two_intersections(a1, b1, a2, b2, k3, b3, expected):
    """
    Тести, де одна пара прямих паралельна, а третя їх перетинає.
    Результатом має бути повідомлення з двома різними точками перетину.
    """
    line1 = SegmentLine.SegmentLine(a1, b1)
    line2 = SegmentLine.SegmentLine(a2, b2)
    line3 = SlopeInterceptLine.SlopeInterceptLine(k3, b3)
    classifier = LineClassifier.LineClassifier(line1, line2, line3)
    result = classifier.classify()

    print(result)

    expected_str = "Прямі перетинаються в двох точках"
    assert expected_str in result, f"Результат '{result}' не містить '{expected_str}'"

    point1, point2 = expected
    common_str1 = f"({point1[0]:.6f}, {point1[1]:.6f})"
    assert common_str1 in result, f"Спільна точка '{common_str1}' не знайдена в результаті '{result}'"
    common_str2 = f"({point2[0]:.6f}, {point2[1]:.6f})"
    assert common_str2 in result, f"Спільна точка '{common_str2}' не знайдена в результаті '{result}'"

# Прямі перетинаються в трьох точках
@pytest.mark.parametrize("a1,b1,a2,b2,k3,b3,expected", [
    # Test 1: Граничний випадок з великими від'ємними значеннями
    (-126, -126, -125, -124, 1, -50,
     ((-38.000000, -88.000000),
      (-37.148594, -87.148594),
      (-250.00000, 124.000000))),

    # Test 2: Типовий випадок з позитивними значеннями
    (100, 90, 80, 100, 1, 50,
     ((28.571429, 64.285714),
      (21.052632, 71.052632),
      (22.222222, 72.222222))),

    # Test 3: Типовий випадок з малими значеннями
    (3, 4, 4, 3, 2, 1,
     ((1.714286, 1.714286),
      (0.727273, 2.454545),
      (0.900000, 2.800000))),

    # Test 4: Спеціальний випадок – комбінація негативних і позитивних параметрів
    (-20, 50, 30, -60, 0.5, 10,
     ((-20.000000, 0.000000),
      (46.666667, 33.333333),
      (-220.000000, -500.000000))),

    # Test 5: Граничний випадок із використанням максимальних значень
    (126, 30, 125, 40, -1, 5,
     ((122.093023, 0.930233),
      (-32.812500, 37.812500),
      (-51.470588, 56.470588))),

    # Test 6: Спеціальний випадок із змішанням малих від'ємних значень та граничними
    (-126, 126, 50, -126, 0.75, -10,
     ((165.789474, 291.789474),
      (-544.000000, -418.000000),
      (65.536723, 39.152542))),
])
def test_three_intersections(a1, b1, a2, b2, k3, b3, expected):
    """
    Тести, де кожна пара прямих перетинається в унікальну точку (3 різні точки перетину).
    Результатом має бути повідомлення, яке містить фразу "Прямі перетинаються в трьох точках"
    та відформатований перелік трьох точок (точність 6 знаків після коми).
    """
    # Створюємо об’єкти прямої
    line1 = SegmentLine.SegmentLine(a1, b1)
    line2 = SegmentLine.SegmentLine(a2, b2)
    line3 = SlopeInterceptLine.SlopeInterceptLine(k3, b3)
    classifier = LineClassifier.LineClassifier(line1, line2, line3)
    result = classifier.classify()

    print(result)

    # Перевірка, що в результаті є фраза для трьох точок
    expected_phrase = "Прямі перетинаються в трьох точках"
    assert expected_phrase in result, f"Результат '{result}' не містить очікувану фразу '{expected_phrase}'"


    # Формуємо рядки для кожної очікуваної точки
    point1, point2, point3 = expected
    common_str1 = f"({point1[0]:.6f}, {point1[1]:.6f})"
    assert common_str1 in result, f"Спільна точка '{common_str1}' не знайдена в результаті '{result}'"
    common_str2 = f"({point2[0]:.6f}, {point2[1]:.6f})"
    assert common_str2 in result, f"Спільна точка '{common_str2}' не знайдена в результаті '{result}'"
    common_str3 = f"({point3[0]:.6f}, {point3[1]:.6f})"
    assert common_str3 in result, f"Спільна точка '{common_str3}' не знайдена в результаті '{result}'"

def test_exit_program_most_left(monkeypatch):
    """
    Тест для перевірки виходу з програми при введенні перших двох чисел -126 та виходу.
    Імітуємо ввід: "-126", "-126", "e"
    """
    inputs = iter(['-126', '-126', 'e'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with pytest.raises(SystemExit):
        app = LinesApp.LinesApp()
        app.run()


def test_exit_program_left(monkeypatch):
    """
    Тест для перевірки виходу з програми при введенні чисел: "-100", "-100", "-120", "-99" та команди виходу "e".
    """
    inputs = iter(['-100', '-100', '-120', '-99', 'e'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with pytest.raises(SystemExit):
        app = LinesApp.LinesApp()
        app.run()


def test_exit_program_average(monkeypatch):
    """
    Тест для перевірки виходу з програми при введенні чисел: "-10", "-10", "10", "-9" та команди виходу "e".
    """
    inputs = iter(['-10', '-10', '10', '-9', 'e'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with pytest.raises(SystemExit):
        app = LinesApp.LinesApp()
        app.run()

def test_exit_program_right(monkeypatch):
    """

    """
    inputs = iter(['120', '120', 'e'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with pytest.raises(SystemExit):
        app = LinesApp.LinesApp()
        app.run()


def test_exit_program_most_right(monkeypatch):
    """
    """
    inputs = iter(['126', '126', 'e'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with pytest.raises(SystemExit):
        app = LinesApp.LinesApp()
        app.run()

###############################################################################
# Група 1. Тести для відсутності вхідного значення або пустого поля
###############################################################################

# Симуляція вводу користувача методом _input_number із застосуванням monkeypatch.
@pytest.mark.parametrize("inputs, expected", [
    (["", "50"], 50.0),           # порожній рядок, потім типове значення
    (["   ", "10"], 10.0),         # лише пробіли, потім "10"
    (["", "126"], 126.0),          # граничне значення з правої межі
    (["", "-126"], -126.0),        # граничне значення з лівої межі
    (["", "0"], 0.0),             # нульове значення — допустиме (якщо це дозволено)
    (["", "100"], 100.0)          # типове значення
])
def test_empty_input(monkeypatch, inputs, expected):
    """
    Перевіряє, що при відсутності вводу (порожній рядок, пробіли) система повторює запит і
    врешті дає коректне числове значення.
    """
    inputs_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs_iter))
    app = LinesApp.LinesApp()
    val = app._input_number("Введіть значення:")
    assert val == expected

# Тести для некоректного формату вводу (нечислові значення)
@pytest.mark.parametrize("inputs", [
    ["abc", "50"],              # текст замість числа
    ["!@#$", "100"],
    ["ten", "10"],
    ["12.34.56", "20"],
    ["", "abc", "30"],          # спочатку порожній, потім некоректний текст, потім валідне значення
    ["   ", "not a number", "126"]
])
def test_invalid_format(monkeypatch, inputs):
    """
    Перевіряє, що якщо користувач вводить некоректний формат (нечислове значення),
    функція _input_number продовжує запит, поки не буде отримано число.
    """
    inputs_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs_iter))
    app = LinesApp.LinesApp()
    val = app._input_number("Введіть значення:")
    # Перевіряємо, що отримане значення є числом
    assert isinstance(val, float)

###############################################################################
# Група 2. Тести для числових значень, що не входять до проміжку [-126;126]
###############################################################################

# Припускаємо, що конструктори класів перевіряють, що значення має бути у проміжку [-126;126] та
# кидати ValueError, якщо це не так.

@pytest.mark.parametrize("a, b", [
    (130, 10),      # a більше верхньої межі
    (-130, 10),     # a нижче нижньої межі
    (10, 130),      # b більше верхньої межі
    (10, -130),     # b нижче нижньої межі
    (127, 0.5),     # a трохи перевищує
    (-127, -1)      # a трохи нижче допустимого
])
def test_segmentline_out_of_range(a, b):
    with pytest.raises(InvalidLineException):
        SegmentLine.SegmentLine(a, b)

@pytest.mark.parametrize("k, b", [
    (130, 10),      # k перевищує верхню межу
    (-130, 10),     # k нижче нижньої межі
    (10, 130),      # b перевищує верхню межу (для SlopeInterceptLine параметр b перевіряємо окремо)
    (10, -130),     # b нижче нижньої межі
    (127, 0.5),     # k трохи перевищує
    (-127, -1)      # k трохи нижче
])
def test_slopeinterceptline_out_of_range(k, b):
    with pytest.raises(InvalidLineException):
        SlopeInterceptLine.SlopeInterceptLine(k, b)

###############################################################################
# Група 3. Тести для некоректного задання прямої: a=0 або b=0 (для рівняння x/a + y/b = 1)
###############################################################################

@pytest.mark.parametrize("a, b", [
    (0, 10),    # a нульовий
    (0, -10),
    (10, 0),    # b нульовий
    (-10, 0),
    (0, 126),
    (126, 0)
])
def test_segmentline_zero_parameters(a, b):
    with pytest.raises(InvalidLineException):
        SegmentLine.SegmentLine(a, b)

###############################################################################
# 4. Тести для некоректного визначення прямих (необчислювані коефіцієнти)
###############################################################################

def test_segmentline_both_zero():
    """
    Якщо для прямої виду x/a + y/b = 1 задано a=0 та b=0,
    коефіцієнти розрахувати неможливо – має бути викликаний InvalidLineException.
    """
    with pytest.raises(InvalidLineException):
        SegmentLine.SegmentLine(0, 0)

def test_slopeinterceptline_b_zero():
    """
    Для прямої виду y = kx + b параметр b не може бути 0.
    """
    with pytest.raises(InvalidLineException):
        SlopeInterceptLine.SlopeInterceptLine(1, 0)


###############################################################################
# 5. Тест для ситуації, коли всі 3 прямі співпадають
###############################################################################

def test_all_three_lines_coincide():
    """
    Якщо всі три прямі задані однаковими параметрами, система вважає це некоректним.
    Припускаємо, що в такому випадку створення класифікатора або виклик classify() кине виняток
    з повідомленням, що "Усі 3 прямі не можуть співпадати".
    """
    with pytest.raises(InvalidLineException, match="Усі 3 прямі не можуть співпадати"):
        line1 = SegmentLine.SegmentLine(-100, -100)
        line2 = SegmentLine.SegmentLine(-100, -100)
        line3 = SlopeInterceptLine.SlopeInterceptLine(-1, -100)
        classifier = LineClassifier.LineClassifier(line1, line2, line3)
        classifier.classify()


###############################################################################
# 6. Тести для ситуації, коли дві прямі задані однаковими точками
###############################################################################

@pytest.mark.parametrize("x1,y1,x2,y2", [
    (10, 20, 10, 20),
    (-50, 60, -50, 60),
    (126, -126, 126, -126),
    (15, 15, 15, 15),
    (-30, 40, -30, 40)
])
def test_line_by_points_identical(x1, y1, x2, y2):
    """
    Якщо дві прямі задано однаковими, має бути кинутий InvalidLineException.
    Очікується повідомлення, яке містить інформацію про те, що точки співпадають.
    """
    with pytest.raises(InvalidLineException, match=".*однаковими.*"):
        line1 = SegmentLine.SegmentLine(x1, y1)
        line2 = SegmentLine.SegmentLine(x2, y2)
        line3 = SlopeInterceptLine.SlopeInterceptLine(1, 10)
        classifier = LineClassifier.LineClassifier(line1, line2, line3)
        classifier.classify()