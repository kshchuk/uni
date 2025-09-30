# Звіт з проєктування: TechMarket Data Platform

Цей звіт документує рішення, діаграми та обґрунтування архітектури для системи збору, трансформації та аналітики продажів. Мета — показати повний шлях даних: від операційних сервісів (мікросервіси) до звітів у BI, із фокусом на безпеку, якість даних і продуктивність.

## Резюме
- Патерн: OLTP → ETL → DWH → BI, із чітким поділом ролей і навантажень.
- Прикладний рівень: мікросервіси (API Gateway / BFF; Auth, Order, Catalog, Payment, Notification).
- OLTP: підхід DB‑per‑service (MySQL) — окремі схеми/БД для Auth/Orders/Catalog/Payments (read‑only для ETL/BI).
- DWH: PostgreSQL 15, зоряна схема (`fact_sales` + `dim_*`), staging (`stg`) для завантажень.
- ETL: Python 3.11 + SQLAlchemy (pandas, psycopg2, PyMySQL), інкрементальні завантаження за watermark, advisory lock, аудит.
- BI: Power BI/Tableau з RLS та read‑only підключенням до DWH.
- Безпека: хешовані паролі, токени доступу/SSO, ролі/доступи.

## Цілі та KPI
- Динаміка продажів за регіонами та категоріями.
- Ефективність менеджерів (revenue, кількість замовлень, середній чек).
- Топ/антитоп товарів (за revenue/quantity).
- Середній чек (AOV) та тренди.

## Відповідність вимогам → артефакти
- MySQL, PostgreSQL — схеми у DBML, рендер ER.
- Python (SQLAlchemy, pandas, psycopg2) — ETL‑потік, sequence‑діаграми.
- Tableau/Power BI — BI use case + RLS підхід.
- Результат — цей звіт + вихідні .sql/.py (плануються) + .puml/.dbml.

## Архітектурні рішення (ADR)
- Поділ OLTP і DWH: OLTP нормалізований (≈3НФ), DWH денормалізований (зоряна схема) заради аналітики.
- Інкрементальні ETL: watermark по `updated_at`/`order_date`, idempotent‑upsert у `dwh`.
- Якість даних: перевірки у `stg` (унікальність, not null, домени), звіти DQ, fail‑fast.
- Безпека: хешовані паролі, токени/сесії, read‑only роль для BI, RLS у BI/БД.
- Продуктивність: COPY у `stg`, індекси на ключах вимірів та `date_key`, матеріалізовані вітрини.

---

## Use Case — Огляд
{{PUML docs/usecase/usecase_overview.puml}}

Коментарі:
- Актори: Керівництво, BI Аналітик, DBA, Планувальник ETL, OLTP як джерело.
- Ключові кейси: Проєктування схем, доступи, ETL‑pipeline, DQ, BI‑звіти, керування користувачами/ролями і токенами.
- Взаємозв’язки: BI включає конкретні KPI; ETL включає DQ; DBA керує доступами та auth.

## Use Case — OLTP
{{PUML docs/usecase/usecase_oltp.puml}}

Коментарі:
- Блок автентифікації: реєстрація, вхід, перевірка/відкликання токенів, скидання пароля.
- Замовлення: оформлення → додавання позицій → знижки → оплата (PSP) → статуси (`new`, `paid`).
- Примітка: `orders.total_amount` — кешований агрегат (підтримується застосунком/тригерами).

## Use Case — ETL / DWH
{{PUML docs/usecase/usecase_etl_dwh.puml}}

Коментарі:
- Pipeline: Extract з OLTP → Load у `stg` → побудова `dim_*` та `fact_sales` → аудит.
- Сервісна автентифікація: перевірка доступу перед запуском (для API‑керованого пайплайну).
- Інкременти: `E5` як розширення pipeline за watermarks (SCD‑1 для простоти).

## Use Case — BI
{{PUML docs/usecase/usecase_bi.puml}}

Коментарі:
- Вхід і авторизація (SSO/токени у реальних інсталяціях), застосування RLS.
- Дашборд включає KPI: тренди, ефективність менеджерів, топ/антитоп, AOV; експорт/публікації.
- DirectQuery/Import — залежить від обсягу даних та SLA оновлень.

---

## Sequence — Оформити замовлення (OLTP)
{{PUML docs/sequence_oltp_place_order.puml}}

Коментарі:
- Рівні: UI → API Gateway → Order/Catalog/Payment/Auth сервіси; асинхронні події через брокер.
- Транзакція: створення `orders` + `order_items`, підрахунок суми; оплата як окремий сервіс.
- Платіж: зовнішній PSP; при успіху — статус `paid` і подія `OrderPaid` для нотифікацій.

## Sequence — Вхід і видача токена (Auth)
{{PUML docs/sequence_auth_login.puml}}

Коментарі:
- Зберігаємо хеш пароля; токени/сесії — із TTL/відкликанням; деталі реалізації залежать від стека.

## Sequence — Щоденний конвеєр ETL
{{PUML docs/sequence_etl_daily.puml}}

Коментарі:
- Захист від гонок: advisory lock у DWH.
- Надійність: idempotent‑upsert у вимірах і фактах; логування й нотифікації.
- DQ: унікальність ключів, not null, доменні множини; fail → алерт і зупинка.

## Activity — Перегляд динаміки продажів у BI
{{PUML docs/activity_bi_sales_trend.puml}}

Коментарі:
- Доступ: RLS/ролі; для Import — refresh/кеш, для DirectQuery — pushdown обчислень у DWH.
- UX: фільтри (регіон/категорія/дати), drill‑down/drill‑through, експорт/підписки.

## Deployment — Розгортання
{{PUML docs/deployment.puml}}

Коментарі:
- Сегментація: App tier (API Gateway + мікросервіси), Data Eng tier (Scheduler/ETL/Message Broker), Data tier (MySQL DB‑per‑service, PostgreSQL DWH).
- Секрети: .env локально або Secret Manager у проді; BI підключається read‑only.
- Інтеграції: PSP/Notifier через HTTPS; моніторинг/логи централізовано.

## Deployment — Спрощено
{{PUML docs/deployment_simple.puml}}

Коментарі:
- Узагальнена схема без портів і конкретних інструментів.
- Показано лише ключові блоки та потоки: Клієнт → Edge → Мікросервіси → MySQL; ETL/BI ↔ DWH; спостережуваність узагальнена.

---

## Схеми даних і нормалізація

### Операційні БД (DB-per-service, DBML → ER)
Auth Service
{{DBML_ER docs/db/auth_mysql.dbml}}

Orders Service
{{DBML_ER docs/db/orders_mysql.dbml}}

Catalog Service
{{DBML_ER docs/db/catalog_mysql.dbml}}

Payment Service
{{DBML_ER docs/db/payments_mysql.dbml}}

Пояснення:
- НФ: ≈3НФ/BCNF; дублювання лише там, де виправдано (наприклад, `orders.total_amount`).
- UUID у MySQL: збереження як CHAR(36) для простоти (альтернатива — BINARY(16)).
- Крос‑посилання між БД: зберігаються як ідентифікатори (без FK між БД), цілісність гарантується застосунком/подіями.
- Індекси: FK/PK + службові (`order_date`, `token_hash`, `expires_at`).

### DWH (DBML → ER)
{{DBML_ER docs/dwh_postgres.dbml}}

Пояснення:
- Зерно факту: один рядок на позицію замовлення (`order_item`).
- Виміри: `dim_product`, `dim_customer`, `dim_employee`, `dim_region`, `dim_date`, `dim_category` (ієрархія).
- SCD‑1: перезапис атрибутів у вимірах; історію можна розширити до SCD‑2 за потреби.
- Продуктивність: індекси по foreign keys, `date_key`; матеріалізовані вітрини для популярних зрізів.

## ER — Спрощено (OLTP)
{{PUML docs/er/er_simple_oltp.puml}}

Коментарі:
- Лише сутності та зв’язки: Customer — Order — OrderItem — Product — Payment.
- Без детальних атрибутів, типів та індексів.

## ER — Спрощено (DWH)
{{PUML docs/er/er_simple_dwh.puml}}

Коментарі:
- Зоряна схема: fact_sales з ключовими вимірами (date, product, customer, employee, region).
- Без переліку полів і технічних колонок.

---

## Нефункціональні вимоги
- Продуктивність: COPY у `stg`, пакетні інсерти, індекси та агрегаційні вітрини.
- Безпека: хешування паролів, токени/сесії, мінімум привілеїв (BI — read‑only), TLS скрізь.
- Якість даних: DQ‑правила, аудит завантажень, повторюваність ETL.
- Експлуатація: моніторинг ETL (статус, тривалість, кількість рядків), алерти.

## Ризики та пом’якшення
- Високе навантаження на OLTP при екстракті → вікна невисокої активності, індекси/курсори.
- Затримка оновлень у BI → план рефрешів, SLA на дані.
- Розростання факту → партиціювання за датою у DWH, архівація.

## Подальші кроки
- Згенерувати DDL із DBML, додати seed‑дані.
- Реалізувати ETL‑скрипти (`etl/*.py`) і базові тести.
- Побудувати дашборди в BI згідно KPI і RLS.

---
Примітка: Зображення генеруються скриптом `scripts/generate_design_report.py` на базі вихідних .puml та .dbml файлів.
