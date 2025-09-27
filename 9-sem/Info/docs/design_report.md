# Звіт з проєктування: TechMarket Data Platform

Цей звіт охоплює основні артефакти етапу проєктування: use case діаграми, послідовності, activity, deployment та ER‑схеми OLTP/DWH.

## Архітектурний огляд
- OLTP: MySQL 8 (замовлення, клієнти, товари, оплати, auth_*).
- DWH: PostgreSQL 15 (stg, dwh; зоряна схема fact_sales + dim_*).
- ETL: Python + SQLAlchemy (pandas, psycopg2, PyMySQL), інкременти за watermark.
- Безпека: bcrypt (паролі), Bearer токени (зберігається SHA‑256 хеш), RLS у BI.

## Use Case — Огляд
![usecase_overview](images/usecase_overview.png)

## Use Case — OLTP
![usecase_oltp](images/usecase_oltp.png)

## Use Case — ETL / DWH
![usecase_etl_dwh](images/usecase_etl_dwh.png)

## Use Case — BI
![usecase_bi](images/usecase_bi.png)

## Sequence — Оформити замовлення (OLTP)
![sequence_oltp_place_order](images/sequence_oltp_place_order.png)

## Sequence — Вхід і видача токена (Auth)
![sequence_auth_login](images/sequence_auth_login.png)

## Sequence — Щоденний конвеєр ETL
`Missing: docs/sequence_etl_daily.puml`

## Activity — Перегляд динаміки продажів у BI
![activity_bi_sales_trend](images/activity_bi_sales_trend.png)

## Deployment — Розгортання
![deployment](images/deployment.png)

## Схема даних — OLTP (з DBML)
![oltp_mysql_er](images/oltp_mysql_er.png)

## Схема даних — DWH (з DBML)
![dwh_postgres_er](images/dwh_postgres_er.png)

---
Примітка: Зображення генеруються скриптом на основі вихідних .puml та .dbml файлів.
