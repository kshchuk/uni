# Інструкція по запуску ETL та інтеграції з Airflow

## Зміст

1. [Запуск ETL вручну](#запуск-etl-вручну)
2. [Запуск з Docker](#запуск-з-docker)
3. [Інтеграція з Apache Airflow](#інтеграція-з-apache-airflow)
4. [Моніторинг та логування](#моніторинг-та-логування)

---

## Запуск ETL вручну

### 1. Встановлення залежностей

```bash
cd etl/
pip install -r requirements.txt

# Або встановити як пакет
pip install -e .
```

### 2. Налаштування конфігурації

Створіть `.env` файл:

```bash
cp .env.example .env
nano .env
```

Налаштуйте параметри підключення до баз даних.

### 3. Запуск ETL

#### Повне завантаження:

```bash
python run_etl.py --mode full
```

#### Інкрементальне завантаження:

```bash
python run_etl.py --mode incremental \
    --start-date 2024-01-01 \
    --end-date 2024-01-31
```

#### З вказаним .env файлом:

```bash
python run_etl.py --mode full \
    --env-file /path/to/.env \
    --log-level DEBUG
```

### 4. Запуск як встановлений пакет

Після `pip install -e .`:

```bash
techmarket-etl --mode full
```

---

## 🐳 Запуск з Docker

### 1. Переконайтесь що TechMarket бази даних запущені:

```bash
docker-compose up -d
```

### 2. Створіть Docker мережу (якщо потрібно):

```bash
docker network create techmarket-network
```

### 3. Запустіть ETL в контейнері:

```bash
# Збудуйте образ
docker build -t techmarket-etl:latest -f etl/Dockerfile .

# Запустіть контейнер
docker run --rm \
    --network techmarket-network \
    --env-file etl/.env \
    techmarket-etl:latest \
    python run_etl.py --mode full
```

---

## Інтеграція з Apache Airflow

### Варіант 1: Швидкий старт з Docker Compose

#### 1. Підготовка:

```bash
# Створіть директорії для Airflow
mkdir -p airflow/dags airflow/logs airflow/plugins airflow/config

# Встановіть AIRFLOW_UID
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

#### 2. Запуск Airflow:

```bash
# Запуск всіх сервісів (включаючи Airflow)
docker-compose -f docker-compose.airflow.yml up -d

# Перевірка статусу
docker-compose -f docker-compose.airflow.yml ps
```

#### 3. Доступ до Airflow UI:

- URL: http://localhost:8080
- Логін: `airflow`
- Пароль: `airflow`

#### 4. Активація DAG:

1. Відкрийте Airflow UI
2. Знайдіть DAG `techmarket_etl_daily`
3. Увімкніть його перемикачем
4. Натисніть "Trigger DAG" для ручного запуску

#### 5. Перегляд логів:

```bash
# Логи scheduler
docker-compose -f docker-compose.airflow.yml logs airflow-scheduler

# Логи webserver
docker-compose -f docker-compose.airflow.yml logs airflow-webserver

# Логи ETL (в Airflow UI)
# DAGs -> techmarket_etl_daily -> Graph -> Клік на task -> View Log
```

### Варіант 2: Встановлення на локальний Airflow

#### 1. Встановлення Airflow:

```bash
# Створіть віртуальне середовище
python -m venv airflow-venv
source airflow-venv/bin/activate

# Встановіть Airflow
pip install "apache-airflow==2.7.3" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.3/constraints-3.12.txt"

# Встановіть провайдери
pip install apache-airflow-providers-postgres apache-airflow-providers-mysql

# Встановіть ETL пакет
pip install -e etl/
```

#### 2. Ініціалізація Airflow:

```bash
# Налаштуйте домашню директорію
export AIRFLOW_HOME=~/airflow

# Ініціалізуйте базу даних
airflow db init

# Створіть користувача
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

#### 3. Копіювання DAG:

```bash
# Скопіюйте DAG файл
cp airflow/dags/techmarket_etl_dag.py ~/airflow/dags/

# Або створіть symlink
ln -s $(pwd)/airflow/dags/techmarket_etl_dag.py ~/airflow/dags/
```

#### 4. Налаштування змінних середовища:

Додайте в `~/airflow/airflow.cfg` або встановіть через UI:

```bash
airflow variables set etl_incremental true
airflow variables set etl_batch_size 1000
```

#### 5. Запуск Airflow:

```bash
# Запустіть webserver (в одному терміналі)
airflow webserver --port 8080

# Запустіть scheduler (в іншому терміналі)
airflow scheduler
```

#### 6. Доступ до UI:

- URL: http://localhost:8080
- Використайте створені credentials

### Структура DAG

```
techmarket_etl_daily (Щоденний)
├── check_source_databases  # Перевірка OLTP баз
├── check_dwh_database      # Перевірка DWH
├── run_etl                 # Інкрементальне завантаження
├── notify_success          # Повідомлення про успіх
└── notify_failure          # Обробка помилок

techmarket_etl_weekly_full (Щотижневий)
├── check_source_databases  # Перевірка OLTP баз
├── check_dwh_database      # Перевірка DWH
├── run_etl                 # Повне завантаження
├── notify_success          # Повідомлення про успіх
└── notify_failure          # Обробка помилок
```

### Розклад виконання

- **Щоденний ETL**: Кожного дня о 02:00 UTC
- **Щотижневий ETL**: Кожної неділі о 03:00 UTC

---

## Моніторинг та логування

### 1. Логи ETL

Логи зберігаються в:
- `etl.log` - локальний файл
- Airflow logs: `airflow/logs/dag_id/task_id/execution_date/`

### 2. Перегляд логів:

```bash
# Tail локальних логів
tail -f etl.log

# Grep для помилок
grep ERROR etl.log

# Перегляд логів в Docker
docker logs -f airflow-scheduler
```

### 3. Моніторинг через Airflow UI:

1. Відкрийте Dashboard
2. Перегляньте стан DAG
3. Клікніть на task для деталей
4. View Log для повних логів

### 4. Метрики ETL:

Airflow автоматично збирає:
- Час виконання кожного task
- Кількість успіхів/помилок
- SLA порушення

### 5. Налаштування сповіщень:

Відредагуйте `techmarket_etl_dag.py`:

```python
# Email сповіщення
DEFAULT_ARGS = {
    'email': ['your.email@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
}

# Або додайте Slack webhook
def send_slack_notification(**context):
    from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
    
    slack_msg = f"✅ ETL completed: {context['task_instance'].dag_id}"
    
    slack_alert = SlackWebhookOperator(
        task_id='slack_notification',
        http_conn_id='slack_webhook',
        message=slack_msg,
    )
    
    return slack_alert.execute(context=context)
```

---

## Troubleshooting

### Помилка підключення до БД:

```bash
# Перевірте чи працюють контейнери
docker-compose ps

# Перевірте логи
docker-compose logs mysql_orders
docker-compose logs postgres_dwh

# Перевірте мережу
docker network inspect techmarket-network
```

### Airflow не бачить ETL пакет:

```bash
# Перевірте чи встановлено пакет
docker exec airflow-scheduler pip list | grep techmarket-etl

# Переустановіть
docker exec airflow-scheduler pip install -e /opt/airflow/etl

# Перезапустіть scheduler
docker-compose -f docker-compose.airflow.yml restart airflow-scheduler
```

### DAG не з'являється в UI:

```bash
# Перевірте помилки парсингу
docker exec airflow-scheduler airflow dags list

# Перевірте логи scheduler
docker-compose -f docker-compose.airflow.yml logs airflow-scheduler | grep ERROR
```

---

## Додаткові ресурси

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [ETL Best Practices](https://www.astronomer.io/guides/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
