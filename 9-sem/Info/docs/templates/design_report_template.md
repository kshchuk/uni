# Звіт з проєктування: TechMarket Data Platform

Цей звіт охоплює основні артефакти етапу проєктування: use case діаграми, послідовності, activity, deployment та ER‑схеми OLTP/DWH.

## Архітектурний огляд
- OLTP: MySQL 8 (замовлення, клієнти, товари, оплати, auth_*).
- DWH: PostgreSQL 15 (stg, dwh; зоряна схема fact_sales + dim_*).
- ETL: Python + SQLAlchemy (pandas, psycopg2, PyMySQL), інкременти за watermark.
- Безпека: bcrypt (паролі), Bearer токени (зберігається SHA‑256 хеш), RLS у BI.

## Use Case — Огляд
{{PUML docs/usecase/usecase_overview.puml}}

## Use Case — OLTP
{{PUML docs/usecase/usecase_oltp.puml}}

## Use Case — ETL / DWH
{{PUML docs/usecase/usecase_etl_dwh.puml}}

## Use Case — BI
{{PUML docs/usecase/usecase_bi.puml}}

## Sequence — Оформити замовлення (OLTP)
{{PUML docs/sequence_oltp_place_order.puml}}

## Sequence — Вхід і видача токена (Auth)
{{PUML docs/sequence_auth_login.puml}}

## Sequence — Щоденний конвеєр ETL
{{PUML docs/sequence_etl_daily.puml}}

## Activity — Перегляд динаміки продажів у BI
{{PUML docs/activity_bi_sales_trend.puml}}

## Deployment — Розгортання
{{PUML docs/deployment.puml}}

## Схема даних — OLTP (з DBML)
{{DBML_ER docs/oltp_mysql.dbml}}

## Схема даних — DWH (з DBML)
{{DBML_ER docs/dwh_postgres.dbml}}

---
Примітка: Зображення генеруються скриптом на основі вихідних .puml та .dbml файлів.
