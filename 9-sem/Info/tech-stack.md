# TechMarket — технічний стек та архітектура рішення

## Резюме
Мета: побудувати повний ланцюг роботи з даними для бізнес‑аналітики продажів — від транзакційної БД до аналітичних звітів. Обрано підхід «OLTP → ETL → DWH → BI» із MySQL як транзакційною БД, PostgreSQL як аналітичним сховищем, Python (SQLAlchemy [PyAlchemy] + pandas; драйвер psycopg2) для ETL та Power BI для візуалізації.

## Архітектура даних (огляд)
- Джерело даних (OLTP): MySQL — операційна система обліку замовлень, клієнтів, товарів.
- Сховище (DWH): PostgreSQL — зоряна схема для аналітики (факт продажів + виміри).
- ETL/ELT: Python 3.11, `SQLAlchemy` (керування підключеннями/ORM), `pandas` (трансформації), драйвери: `psycopg2` (PostgreSQL), `PyMySQL` (MySQL).
- BI: Power BI (рекомендовано) або Tableau — підключення напряму до PostgreSQL (read‑only).

## Компоненти стеку і версії
- MySQL 8.x — OLTP, зразки даних та початкові `.sql` скрипти.
- PostgreSQL 15.x — DWH та аналітика.
- Python 3.11+
  - SQLAlchemy ≥ 2.0
  - pandas ≥ 2.0
  - psycopg2-binary ≥ 2.9
  - PyMySQL ≥ 1.0 (для MySQL через SQLAlchemy)
  - python-dotenv (керування секретами через `.env`)
- BI: Power BI Desktop (альтернатива — Tableau Desktop).

Примітка: Використовуємо SQLAlchemy як основний шар підключень: `postgresql+psycopg2://...` та `mysql+pymysql://...`. За потреби допускається експорт у CSV (`SELECT ... INTO OUTFILE`/`mysqldump`) як fallback.

## Моделювання даних
- OLTP (MySQL):
  - `customers`, `regions`
  - `employees` (менеджери),
  - `categories`, `products`
  - `orders` (order_id, customer_id, employee_id, order_date, region_id, total_amount, status)
  - `order_items` (order_id, product_id, quantity, unit_price, discount)
  - `payments` (order_id, method, paid_at, amount)
- DWH (PostgreSQL, зоряна схема):
  - Факт: `fact_sales` (order_id, order_item_id, date_key, product_key, customer_key, employee_key, region_key, quantity, revenue, discount_amount, cost, margin)
  - Виміри: `dim_date`, `dim_product`, `dim_customer`, `dim_employee`, `dim_region`, `dim_category`
  - Сурогатні ключі, SCD‑тип 1 для простої реалізації, перевірки цілісності та індекси по ключових полях.

## Аналітичні показники (KPI)
- Динаміка продажів: сума `revenue` за датами/регіонами/категоріями.
- Ефективність менеджерів: `revenue`, кількість замовлень/позицій, середній чек на менеджера.
- Топ/N найпопулярніші товари: за `revenue` та `quantity`.
- Найменш популярні товари: ті ж метрики у зворотному рейтингу.
- Середній чек: `revenue / distinct_orders`.

## Потік даних (ETL)
1) Extract: через SQLAlchemy з MySQL (`mysql+pymysql`) у pandas DataFrame; для великих обсягів можливий експорт у CSV/staging.
2) Load: завантаження у PostgreSQL через `COPY` (psycopg2) з підключення SQLAlchemy або `pandas.to_sql` для невеликих датасетів у `stg.*` таблиці.
3) Transform: побудова `dim_*` і `fact_sales` у схемі `dwh` за допомогою `pandas` та SQL‑трансформацій (SQLAlchemy Core/DDL).
4) Serve: підключення BI до `dwh` (read‑only роль).

## DBML схеми та генерація SQL
- OLTP (MySQL): `docs/oltp_mysql.dbml`
- DWH (PostgreSQL): `docs/dwh_postgres.dbml`

Опціонально, згенерувати SQL зі схем DBML (приклад з `@dbml/cli`):
```
# MySQL DDL
dbml2sql docs/oltp_mysql.dbml --mysql -o sql/mysql/01_schema.sql

# PostgreSQL DDL
dbml2sql docs/dwh_postgres.dbml --postgres -o sql/postgres/01_dwh_schema.sql
```

## Нотатки з архітектури та практик
- Інкрементальні завантаження: відбір змінених записів за `updated_at`/`order_date` + водяні знаки завантажень у службовій таблиці `dwh.load_watermarks`.
- Якість даних: валідації на етапі `stg` (унікальність ключів, доменні обмеження, not null), логування відхилених рядків.
- Продуктивність: індекси по `date_key`, `product_key`, `customer_key`, `employee_key`, `region_key`; агрегаційні вітрини у `03_views_marts.sql`.
- Безпека: окрема роль для BI з правами `SELECT` на `dwh.*`.
