# Instructions
- The user will provide a task.
- Wait for all terminal commands to be completed (or terminate them) before finishing.

Ось повний `INSTRUCTIONS.md`, перероблений під **Python-бібліотеку**. Я зробив його у форматі, який ти зможеш одразу використати в codex або як internal guideline.

---

# Python Library Development Guidelines

## 0. **Design Patterns**

* Використовуй відповідні патерни для розділення відповідальності:

  * **Factory / Builder** — для створення об’єктів (алгоритмів оптимізації, моделей).
  * **Strategy** — для різних методів оптимізації (градієнтний спуск, CMA-ES, тощо).
  * **Observer** — для логування, callback’ів, моніторингу.
  * **Adapter** — щоб узгодити API сторонніх бібліотек з єдиним інтерфейсом.
* Уникай "God objects", глибоких `if-else` дерев та жорстких залежностей.
* Код повинен бути **тестованим та розширюваним**.

---

## 1. **Python Style Guide**

* Дотримуйся **PEP8**:

  * `PascalCase` — для класів (`GradientDescent`, `LineSearch`).
  * `snake_case` — для функцій та змінних (`compute_step`, `grad_norm`).
  * `CONSTANT_CASE` — для констант (`MAX_ITER`, `DEFAULT_ALPHA`).
* Максимальна довжина рядка — 88 символів (як у Black).
* Використовуй 4 пробіли для відступів (без табів).
* Кожен модуль має `__all__` для чіткого API.

---

## 2. **Type Hints & Contracts**

* Усі публічні методи повинні мати **type hints**.
* Використовуй `typing` (`Callable`, `Protocol`, `Union`, `Optional`).
* Для складних структур — окремі `TypedDict` або `dataclasses`.

---

## 3. **SOLID & OOP**

* **Single Responsibility** — кожен клас робить тільки одну річ.
* **Open/Closed** — алгоритми оптимізації можна додавати без зміни базового коду.
* **Liskov Substitution** — усі оптимізатори мають спільний базовий інтерфейс.
* **Interface Segregation** — відокремлюй інтерфейси (наприклад, `Optimizer`, `Visualizer`).
* **Dependency Inversion** — залеж від абстракцій, а не від конкретних реалізацій.

---

## 4. **Documentation**

* Використовуй **Google-стиль docstrings** (підтримується `sphinx.ext.napoleon`).
* Кожен публічний клас і метод має:

  ```python
  def step(self, x: np.ndarray) -> np.ndarray:
      """
      Perform one optimization step.

      Args:
          x (np.ndarray): Current point.

      Returns:
          np.ndarray: Updated point.
      """
  ```
* Для групування — модулі `@defgroup` (наприклад, `@defgroup optimizers`).

---

## 5. **Testing**

* Використовуй `pytest`.
* Покриття тестами ≥ 80%.
* Unit-тести окремо для:

  * математичних функцій,
  * оптимізаторів,
  * візуалізацій.

---

## 6. **Error Handling**

* Використовуй **чіткі винятки** (`ValueError`, `TypeError`, `RuntimeError`).
* Не використовуй "тихе" ігнорування помилок.
* Винятки мають пояснювати проблему (`raise ValueError("Step size must be > 0")`).

---

## 7. **Performance & Constraints**

* Використовуй **NumPy / SciPy** для обчислень.
* Уникай зайвих циклів (векторизація).
* Для великих задач — підтримка JAX/Numba (через адаптери).
* Ніякої рекурсії для критичних алгоритмів.

---

## 8. **Visualization**

* Використовуй **Plotly** для інтерактивних графіків.
* Використовуй **Matplotlib** для експорту (PDF, PNG, MP4).
* Візуалізація повинна бути окремим модулем (`visualization/`), без жорсткої залежності від оптимізаторів.

---

## 9. **Project Organization**

```
my_optimizer_lib/
│
├── optimizers/        # Алгоритми (GradientDescent, CMAES, etc.)
│   ├── base.py        # Абстрактний Optimizer
│   ├── gradient_descent.py
│   └── ...
│
├── line_search/       # Правила (Backtracking, Armijo, Wolfe)
│
├── visualization/     # Plotly / Matplotlib інструменти
│
├── utils/             # math, logging, type helpers
│
├── tests/             # pytest тести
│
├── examples/          # ноутбуки / демо
│
├── __init__.py
└── setup.py
```

## 10. Documentation

* Усі коментарі та документація має бути англійською мовою

---


