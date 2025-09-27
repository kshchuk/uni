import numpy as np
import pandas as pd
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# 1) Створюємо синтетичний датасет:
#    - 1000 зразків
#    - 20 ознак (X1…X20)
#    - шум noise=10 для невеликої “нерегулярності”
X, y = make_regression(
    n_samples=1000,
    n_features=20,
    noise=10.0,
    random_state=42
)
df = pd.DataFrame(X, columns=[f"X{i}" for i in range(1, 21)])
df["Y"] = y

# 2) Розбиваємо на тренувальну й тестову вибірки (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    df.drop("Y", axis=1),
    df["Y"],
    test_size=0.2,
    random_state=42
)

# 3) Навчаємо лінійну регресію
model = LinearRegression()
model.fit(X_train, y_train)

# 4) Прогнозуємо на тренувальній вибірці
y_train_pred = model.predict(X_train)

# 5) Обчислюємо R² (коефіцієнт детермінації) на тренувальній вибірці
r2_train = r2_score(y_train, y_train_pred)
print(f"R² на тренувальній вибірці: {r2_train:.4f}")
