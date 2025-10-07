# TechMarket Database Infrastructure - Повна документація

## Огляд проекту

TechMarket - це мікросервісна система управління інтернет-магазином з паттерном Database-per-Service. Кожен сервіс має власну базу даних для забезпечення незалежності та масштабованості.

### Бази даних

- **Auth DB (MySQL 8.0)** - автентифікація та авторизація користувачів
- **Catalog DB (MySQL 8.0)** - каталог товарів та категорій
- **Orders DB (MySQL 8.0)** - замовлення, клієнти, менеджери, регіони
- **Payments DB (MySQL 8.0)** - обробка платежів
- **DWH DB (PostgreSQL 15)** - сховище даних для аналітики (Star Schema)

## Документація

- **[DATABASE_README.md](DATABASE_README.md)** - Детальна інструкція по роботі з Docker Compose
- **[KUBERNETES_README.md](KUBERNETES_README.md)** - Детальна інструкція по деплою в Kubernetes
- **[LAB_REPORT.md](LAB_REPORT.md)** - Повний звіт з етапами виконання лабораторної роботи
- **[SCREENSHOT_INSTRUCTIONS.md](SCREENSHOT_INSTRUCTIONS.md)** - Інструкції для створення скріншотів

## Швидкий старт

### Docker Compose (для розробки)

```bash
# 1. Запустити всі бази даних
docker-compose up -d

# 2. Встановити Python залежності
pip install -r database/data/requirements.txt

# 3. Згенерувати тестові дані
python3 database/data/generate_test_data.py

# 4. Відкрити Adminer
open http://localhost:8080
```

### Kubernetes (для production)

```bash
# 1. Створити namespace та secrets
kubectl apply -f k8s/00-namespace-secrets.yaml

# 2. Створити ConfigMaps
./k8s/create-configmaps.sh

# 3. Розгорнути бази даних
kubectl apply -f k8s/mysql/
kubectl apply -f k8s/postgres/

# 4. Перевірити статус
kubectl get pods -n techmarket
```

### Makefile команди

```bash
make setup        # Повне налаштування (Docker + дані)
make start        # Запустити бази даних
make stop         # Зупинити бази даних
make restart      # Перезапустити
make logs         # Переглянути логи
make clean        # Очистити все
make ps           # Статус контейнерів
make data         # Згенерувати дані
make test         # Перевірити з'єднання
make backup       # Створити backup
make adminer      # Відкрити Adminer
make k8s-deploy   # Деплой в K8s
make k8s-clean    # Видалити з K8s
```

## Структура проекту

```
Info/
├── docker-compose.yml              # Docker Compose конфігурація
├── Makefile                        # Команди для управління
├── DATABASE_README.md              # Docker документація
├── KUBERNETES_README.md            # K8s документація
├── LAB_REPORT.md                   # Лабораторний звіт
├── SCREENSHOT_INSTRUCTIONS.md      # Інструкції для скріншотів
│
├── database/
│   ├── init/                       # SQL схеми (згенеровані)
│   │   ├── 01_auth_schema.sql
│   │   ├── 02_catalog_schema.sql
│   │   ├── 03_orders_schema.sql
│   │   ├── 04_payments_schema.sql
│   │   └── 05_dwh_schema.sql
│   └── data/
│       ├── generate_test_data.py   # Генератор тестових даних
│       └── requirements.txt        # Python залежності
│
├── docs/
│   ├── db/                         # DBML схеми (вихідні)
│   │   ├── auth_mysql.dbml
│   │   ├── catalog_mysql.dbml
│   │   ├── orders_mysql.dbml
│   │   ├── payments_mysql.dbml
│   │   └── dwh_postgres.dbml
│   ├── er/                         # ER діаграми (PlantUML)
│   │   ├── auth_er.puml
│   │   ├── catalog_er.puml
│   │   ├── orders_er.puml
│   │   ├── payments_er.puml
│   │   └── dwh_er.puml
│   ├── images/                     # Згенеровані зображення діаграм
│   └── report-screenshots/         # Дані для звіту
│
├── k8s/                            # Kubernetes manifests
│   ├── 00-namespace-secrets.yaml   # Namespace та Secrets
│   ├── create-configmaps.sh        # Скрипт створення ConfigMaps
│   ├── mysql/                      # MySQL StatefulSets
│   │   ├── 01-auth-db.yaml
│   │   ├── 02-catalog-db.yaml
│   │   ├── 03-orders-db.yaml
│   │   └── 04-payments-db.yaml
│   └── postgres/                   # PostgreSQL StatefulSet
│       └── 05-dwh-db.yaml
│
└── scripts/                        # Допоміжні скрипти
    ├── setup_databases.sh          # Автоматичне налаштування
    └── generate-report-data.sh     # Збір даних для звіту
```

## Технології

- **DBML** - Database Markup Language для опису схем
- **MySQL 8.0** - Реляційна СУБД для OLTP операцій
- **PostgreSQL 15** - Реляційна СУБД для OLAP аналітики
- **Docker & Docker Compose** - Контейнеризація
- **Kubernetes** - Оркестрація контейнерів
- **Python 3** - Мова для скриптів автоматизації
- **Faker** - Генерація реалістичних тестових даних
- **Adminer** - Веб-інтерфейс для управління БД

## Доступ до баз даних

### Docker Compose порти

| База даних | Хост | Порт | Користувач | Пароль | Database |
|-----------|------|------|------------|---------|----------|
| Auth DB | localhost | 3306 | auth_user | auth_pass | auth_db |
| Catalog DB | localhost | 3307 | catalog_user | catalog_pass | catalog_db |
| Orders DB | localhost | 3308 | orders_user | orders_pass | orders_db |
| Payments DB | localhost | 3309 | payments_user | payments_pass | payments_db |
| DWH DB | localhost | 5432 | dwh_user | dwh_pass | dwh_db |
| Adminer | localhost | 8080 | - | - | - |

### Підключення через CLI

```bash
# MySQL
mysql -h localhost -P 3306 -u auth_user -pauth_pass auth_db

# PostgreSQL
psql -h localhost -p 5432 -U dwh_user -d dwh_db
# Password: dwh_pass
```

### Kubernetes (через port-forward)

```bash
# Auth DB
kubectl port-forward -n techmarket svc/auth-db 3306:3306

# DWH DB
kubectl port-forward -n techmarket svc/dwh-db 5432:5432
```

## Тестові дані

Генератор створює:
- **5 регіонів** - Київська, Львівська, Одеська, Харківська, Дніпропетровська
- **14 категорій** - 6 головних + 8 підкатегорій
- **25 товарів** - ноутбуки, смартфони, периферія, аксесуари
- **10 співробітників** - з яких 5 менеджерів
- **50 клієнтів**
- **600 замовлень** - зі статусами new, paid, shipped, cancelled
- **540+ платежів** - card, paypal, bank_transfer, cash
- **61 користувач** - клієнти + співробітники + адміністратор
- **4 ролі** - ADMIN, SALES, CUSTOMER, BI_VIEWER

## Корисні команди

### Docker

```bash
# Логи
docker-compose logs -f auth-db

# Виконання команди в контейнері
docker-compose exec auth-db mysql -u root -prootpass

# Backup
docker-compose exec auth-db mysqldump -u root -prootpass auth_db > backup.sql

# Restore
docker-compose exec -T auth-db mysql -u root -prootpass auth_db < backup.sql
```

### Kubernetes

```bash
# Логи
kubectl logs -f auth-db-0 -n techmarket

# Exec в pod
kubectl exec -it auth-db-0 -n techmarket -- bash

# Backup
kubectl exec auth-db-0 -n techmarket -- \
  mysqldump -u root -prootpass auth_db > backup.sql

# Port forward всіх БД
kubectl port-forward -n techmarket svc/auth-db 3306:3306 &
kubectl port-forward -n techmarket svc/catalog-db 3307:3306 &
kubectl port-forward -n techmarket svc/orders-db 3308:3306 &
kubectl port-forward -n techmarket svc/payments-db 3309:3306 &
kubectl port-forward -n techmarket svc/dwh-db 5432:5432 &
```

## Troubleshooting

### База даних не стартує в Docker

```bash
# Перевірити логи
docker-compose logs auth-db

# Перезапустити
docker-compose restart auth-db

# Повне перестворення
docker-compose down -v
docker-compose up -d
```

### Pod pending в Kubernetes

```bash
# Перевірити причину
kubectl describe pod auth-db-0 -n techmarket

# Перевірити PVC
kubectl get pvc -n techmarket

# Перевірити events
kubectl get events -n techmarket --sort-by='.lastTimestamp'
```

### Помилка генерації даних

```bash
# Перевірити з'єднання
docker-compose exec auth-db mysqladmin ping

# Перевірити таблиці
docker-compose exec auth-db mysql -u auth_user -pauth_pass auth_db -e "SHOW TABLES;"
```

## Архітектура

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│                     (Adminer, CLI tools)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Container Orchestration                    │
│              (Docker Compose / Kubernetes)                   │
└────┬────────┬─────────┬─────────┬─────────┬────────────────┘
     │        │         │         │         │
┌────▼───┐┌──▼────┐┌───▼────┐┌──▼─────┐┌──▼─────┐
│Auth DB ││Catalog││Orders  ││Payments││  DWH   │
│MySQL   ││MySQL  ││MySQL   ││MySQL   ││Postgres│
│:3306   ││:3307  ││:3308   ││:3309   ││:5432   │
└────────┘└───────┘└────────┘└────────┘└────────┘
     │        │         │         │         │
┌────▼────────▼─────────▼─────────▼─────────▼────┐
│              Persistent Storage                  │
│        (Docker Volumes / K8s PVC)                │
└──────────────────────────────────────────────────┘
```

## Вимоги

### Мінімальні

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM
- 20GB disk space

### Для Kubernetes

- Kubernetes 1.24+
- kubectl
- 6GB RAM
- StorageClass для dynamic provisioning

### Для генерації даних

- Python 3.9+
- pip
- 100MB+ вільного місця для даних

## Ліцензія

Цей проект створено для навчальних цілей.

## Автор

Кіщук Ярослав  
Дата: 7 жовтня 2025

---

**Статус проекту:** Виконано ✓

**Версія:** 1.0.0
