# Швидкий старт TechMarket ETL

> Мінімальна інструкція для запуску ETL pipeline за 5 хвилин

## Перед початком

Переконайтесь, що у вас запущені:
- MySQL з базами: `tech_market_auth`, `tech_market_catalog`, `tech_market_orders`, `tech_market_payments`
- PostgreSQL з базою: `tech_market_dwh`

## Крок 1: Активація віртуального середовища

```bash
cd /home/yaroslav/study/uni/9-sem/Info
source env/bin/activate
```

## Крок 2: Перевірка залежностей

```bash
# Якщо потрібно, встановіть залежності
pip install -r etl/requirements.txt
```

## Крок 3: Налаштування підключень

Створіть файл `.env` в кореневій папці проекту:

```bash
cat > .env << 'EOF'
# OLTP Databases (MySQL)
AUTH_DB_HOST=localhost
AUTH_DB_PORT=3306
AUTH_DB_NAME=tech_market_auth
AUTH_DB_USER=root
AUTH_DB_PASSWORD=your_password

CATALOG_DB_HOST=localhost
CATALOG_DB_PORT=3306
CATALOG_DB_NAME=tech_market_catalog
CATALOG_DB_USER=root
CATALOG_DB_PASSWORD=your_password

ORDERS_DB_HOST=localhost
ORDERS_DB_PORT=3306
ORDERS_DB_NAME=tech_market_orders
ORDERS_DB_USER=root
ORDERS_DB_PASSWORD=your_password

PAYMENTS_DB_HOST=localhost
PAYMENTS_DB_PORT=3306
PAYMENTS_DB_NAME=tech_market_payments
PAYMENTS_DB_USER=root
PAYMENTS_DB_PASSWORD=your_password

# DWH Database (PostgreSQL)
DWH_DB_HOST=localhost
DWH_DB_PORT=5432
DWH_DB_NAME=tech_market_dwh
DWH_DB_USER=postgres
DWH_DB_PASSWORD=your_password

# ETL Configuration (опційно)
ETL_BATCH_SIZE=1000
ETL_MAX_WORKERS=4
EOF
```

**⚠️ Важливо:** Замініть `your_password` на реальні паролі!

## Крок 4: Запуск ETL

### Варіант A: Повне завантаження (перший раз)

```bash
python etl/run_etl.py --mode full
```

Це завантажить:
- ✅ Календар (dim_date) - 365+ записів
- ✅ Регіони (dim_region)
- ✅ Категорії (dim_category)
- ✅ Продукти (dim_product)
- ✅ Клієнти (dim_customer)
- ✅ Співробітники (dim_employee)
- ✅ Факти продажів (fact_sales)

**Очікуваний час виконання:** 2-5 хвилин

### Варіант B: Інкрементальне завантаження

Для щоденних оновлень:

```bash
# За останні 7 днів
python etl/run_etl.py --mode incremental --days 7

# За конкретний період
python etl/run_etl.py --mode incremental \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

**Очікуваний час виконання:** 10-30 секунд

## Крок 5: Перевірка результатів

```bash
# Увійдіть в PostgreSQL
psql -h localhost -U postgres -d tech_market_dwh

# Перевірте кількість записів
SELECT 'dim_date' as table, COUNT(*) FROM dim_date
UNION ALL SELECT 'dim_region', COUNT(*) FROM dim_region
UNION ALL SELECT 'dim_category', COUNT(*) FROM dim_category
UNION ALL SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL SELECT 'dim_employee', COUNT(*) FROM dim_employee
UNION ALL SELECT 'fact_sales', COUNT(*) FROM fact_sales;
```

Очікувані результати (приблизно):
```
   table      | count
--------------+-------
 dim_date     |   730
 dim_region   |    10
 dim_category |    50
 dim_product  |  1000
 dim_customer |  5000
 dim_employee |   100
 fact_sales   | 50000
```

## sШвидкі команди

```bash
# Перегляд логів
tail -f etl.log

# Тести (перевірка що все працює)
pytest etl/tests/ -v

# Coverage звіт
pytest --cov=etl --cov-report=html etl/tests/

# Приклади використання
python etl/examples.py
```

## Наступні кроки

### 1. Автоматизація з Airflow (рекомендовано)

```bash
# Запуск Airflow через Docker Compose
docker-compose -f docker-compose.airflow.yml up -d

# Відкрити UI
open http://localhost:8080
# Логін: airflow / Пароль: airflow
```

Детальна інструкція: [AIRFLOW_SETUP.md](AIRFLOW_SETUP.md)

### 2. Моніторинг та аналітика

- Підключіть Power BI / Tableau до PostgreSQL DWH
- Створіть дашборди для моніторингу продажів
- Налаштуйте алерти при проблемах з ETL

### 3. Оптимізація продуктивності

```env
# В .env файлі
ETL_BATCH_SIZE=5000     # Збільшіть для великих обсягів
ETL_MAX_WORKERS=8       # Використайте всі CPU
```

## Додаткова документація

- [Детальний README](etl/README.md) - Повна документація модулів
- [Інтеграція з Airflow](AIRFLOW_SETUP.md) - Налаштування автоматизації
- [Архітектура системи](docs/design_report.md) - Технічний дизайн
- [Приклади коду](etl/examples.py) - 5 практичних прикладів

## Чеклист успішного запуску

- [ ] Віртуальне середовище активовано
- [ ] Всі залежності встановлені
- [ ] Файл `.env` створено і налаштовано
- [ ] MySQL бази даних доступні
- [ ] PostgreSQL DWH доступний
- [ ] Схема DWH створена (05_dwh_schema.sql)
- [ ] Тестові дані згенеровані (опційно)
- [ ] Повне завантаження виконано успішно
- [ ] Записи з'явились у DWH
- [ ] Логи не містять помилок
