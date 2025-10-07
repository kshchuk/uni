# TechMarket Database Infrastructure

Повна інфраструктура баз даних для системи TechMarket з підтримкою Docker Compose та Kubernetes.

## 📋 Огляд

Система використовує мікросервісну архітектуру з окремими базами даних для кожного сервісу (Database-per-Service pattern):

- **Auth DB** (MySQL) - автентифікація та авторизація
- **Catalog DB** (MySQL) - каталог товарів та категорій
- **Orders DB** (MySQL) - замовлення, клієнти, менеджери
- **Payments DB** (MySQL) - платежі
- **DWH DB** (PostgreSQL) - сховище даних для аналітики

## 🚀 Швидкий старт (Docker Compose)

### Передумови

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.9+ (для генерації тестових даних)

### Крок 1: Запуск баз даних

```bash
# Запустити всі бази даних
docker-compose up -d

# Перевірити статус
docker-compose ps

# Переглянути логи
docker-compose logs -f
```

### Крок 2: Підготовка Python середовища

```bash
# Створити віртуальне середовище
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate  # Windows

# Встановити залежності
pip install -r database/data/requirements.txt
```

### Крок 3: Генерація тестових даних

```bash
# Дочекатися повного запуску всіх баз даних (30-60 сек)
sleep 60

# Запустити генератор даних
python3 database/data/generate_test_data.py
```

### Крок 4: Доступ до баз даних

**Через Adminer (Web UI):**
- URL: http://localhost:8080
- Виберіть тип БД, введіть credentials з таблиці нижче

**Через командну строку:**

```bash
# MySQL (Auth DB)
mysql -h localhost -P 3306 -u auth_user -pauth_pass auth_db

# MySQL (Catalog DB)
mysql -h localhost -P 3307 -u catalog_user -pcatalog_pass catalog_db

# MySQL (Orders DB)
mysql -h localhost -P 3308 -u orders_user -porders_pass orders_db

# MySQL (Payments DB)
mysql -h localhost -P 3309 -u payments_user -ppayments_pass payments_db

# PostgreSQL (DWH)
psql -h localhost -p 5432 -U dwh_user -d dwh_db
# Password: dwh_pass
```

### Credentials

| База даних | Хост | Порт | Користувач | Пароль | Database |
|-----------|------|------|------------|---------|----------|
| Auth DB | localhost | 3306 | auth_user | auth_pass | auth_db |
| Catalog DB | localhost | 3307 | catalog_user | catalog_pass | catalog_db |
| Orders DB | localhost | 3308 | orders_user | orders_pass | orders_db |
| Payments DB | localhost | 3309 | payments_user | payments_pass | payments_db |
| DWH DB | localhost | 5432 | dwh_user | dwh_pass | dwh_db |

### Зупинка та очищення

```bash
# Зупинити контейнери
docker-compose stop

# Зупинити та видалити контейнери
docker-compose down

# Видалити контейнери ТА дані
docker-compose down -v
```

## ☸️ Розгортання в Kubernetes

### Передумови

- Kubernetes cluster (minikube, kind, або cloud provider)
- kubectl налаштований для доступу до кластера

### Крок 1: Застосувати конфігурацію

```bash
# Створити namespace та secrets
kubectl apply -f k8s/00-namespace-secrets.yaml

# Створити ConfigMaps з SQL скриптами
chmod +x k8s/create-configmaps.sh
./k8s/create-configmaps.sh

# Розгорнути MySQL бази даних
kubectl apply -f k8s/mysql/

# Розгорнути PostgreSQL DWH
kubectl apply -f k8s/postgres/
```

### Крок 2: Перевірити статус

```bash
# Перевірити pod'и
kubectl get pods -n techmarket

# Перевірити сервіси
kubectl get svc -n techmarket

# Переглянути логи
kubectl logs -n techmarket <pod-name> -f
```

### Крок 3: Доступ до баз даних

**Port forwarding для локального доступу:**

```bash
# Auth DB
kubectl port-forward -n techmarket svc/auth-db 3306:3306

# Catalog DB
kubectl port-forward -n techmarket svc/catalog-db 3307:3306

# Orders DB
kubectl port-forward -n techmarket svc/orders-db 3308:3306

# Payments DB
kubectl port-forward -n techmarket svc/payments-db 3309:3306

# DWH DB
kubectl port-forward -n techmarket svc/dwh-db 5432:5432
```

### Очищення

```bash
# Видалити всі ресурси
kubectl delete namespace techmarket
```

## 📊 Тестові дані

Генератор створює наступні дані:

- **Регіони**: 5 (Київська, Львівська, Одеська, Харківська, Дніпропетровська)
- **Категорії**: 14 (6 головних + 8 підкатегорій)
- **Товари**: 25+
- **Співробітники**: 10 (5 менеджерів)
- **Клієнти**: 50+
- **Замовлення**: 600+
- **Платежі**: ~500 (для paid та shipped замовлень)
- **Користувачі**: 61 (50 клієнтів + 10 співробітників + 1 адмін)
- **Ролі**: 4 (ADMIN, SALES, CUSTOMER, BI_VIEWER)

## 🔧 Корисні команди

### Docker Compose

```bash
# Перезапустити певний сервіс
docker-compose restart auth-db

# Переглянути логи певного сервісу
docker-compose logs -f orders-db

# Виконати команду в контейнері
docker-compose exec auth-db mysql -u root -prootpass -e "SHOW DATABASES;"

# Резервне копіювання
docker-compose exec auth-db mysqldump -u root -prootpass auth_db > backup_auth.sql
docker-compose exec dwh-db pg_dump -U dwh_user dwh_db > backup_dwh.sql

# Відновлення
docker-compose exec -T auth-db mysql -u root -prootpass auth_db < backup_auth.sql
docker-compose exec -T dwh-db psql -U dwh_user dwh_db < backup_dwh.sql
```

### Kubernetes

```bash
# Масштабування (не рекомендується для StatefulSet з БД)
kubectl scale statefulset auth-db -n techmarket --replicas=1

# Exec в pod
kubectl exec -it -n techmarket auth-db-0 -- mysql -u root -prootpass

# Перегляд persistent volumes
kubectl get pv
kubectl get pvc -n techmarket

# Перегляд секретів
kubectl get secrets -n techmarket
kubectl describe secret mysql-secrets -n techmarket
```

## 📁 Структура проекту

```
.
├── docker-compose.yml              # Docker Compose конфігурація
├── database/
│   ├── init/                       # SQL схеми (генеруються з DBML)
│   │   ├── 01_auth_schema.sql
│   │   ├── 02_catalog_schema.sql
│   │   ├── 03_orders_schema.sql
│   │   ├── 04_payments_schema.sql
│   │   └── 05_dwh_schema.sql
│   └── data/
│       ├── generate_test_data.py   # Генератор тестових даних
│       └── requirements.txt        # Python залежності
├── k8s/
│   ├── 00-namespace-secrets.yaml   # Namespace та Secrets
│   ├── create-configmaps.sh        # Скрипт створення ConfigMaps
│   ├── mysql/                      # MySQL StatefulSets
│   │   ├── 01-auth-db.yaml
│   │   ├── 02-catalog-db.yaml
│   │   ├── 03-orders-db.yaml
│   │   └── 04-payments-db.yaml
│   └── postgres/                   # PostgreSQL StatefulSet
│       └── 05-dwh-db.yaml
└── docs/
    ├── db/                         # DBML схеми
    └── er/                         # ER діаграми
```

## 🛠️ Troubleshooting

### База даних не стартує

```bash
# Перевірити логи
docker-compose logs <service-name>

# Видалити volume та перезапустити
docker-compose down -v
docker-compose up -d
```

### Помилка при генерації даних

```bash
# Перевірити чи всі БД запущені
docker-compose ps

# Перевірити connectivity
docker-compose exec auth-db mysqladmin ping

# Перезапустити генератор з debug
python3 database/data/generate_test_data.py
```

### ConfigMap не створюється в K8s

```bash
# Перевірити наявність SQL файлів
ls -la database/init/

# Створити ConfigMap вручну
kubectl create configmap auth-db-init-script \
    --from-file=database/init/01_auth_schema.sql \
    --namespace=techmarket
```

## 📚 Додаткова інформація

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Kubernetes StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [MySQL Docker Hub](https://hub.docker.com/_/mysql)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [DBML Documentation](https://dbml.dbdiagram.io/docs/)

## 📝 Ліцензія

Цей проект створено для навчальних цілей.
