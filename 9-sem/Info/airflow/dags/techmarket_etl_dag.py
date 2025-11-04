"""
Apache Airflow DAG для TechMarket ETL Pipeline.

Цей DAG виконує щоденне інкрементальне завантаження даних
з OLTP баз даних у DWH.

Розклад: Запуск щодня о 02:00 UTC
Автор: Yaroslav Kischuk
"""

from datetime import datetime, timedelta
from typing import Any

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable

# Імпорт ETL модулів (припускаємо що etl пакет доступний)
try:
    from etl.config import ETLConfig
    from etl.pipeline import ETLPipeline
    ETL_AVAILABLE = True
except ImportError:
    ETL_AVAILABLE = False
    print("⚠️  ETL пакет не знайдено. Переконайтесь що він встановлений.")


# Налаштування DAG
DEFAULT_ARGS = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['yaroslav.kischuk@student.uzhnu.edu.ua'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# Змінні Airflow (можна налаштувати через UI)
# Приклад встановлення через CLI:
# airflow variables set etl_incremental true
# airflow variables set etl_batch_size 1000


def check_source_databases(**context: Any) -> None:
    """Перевіряє доступність джерельних баз даних.
    
    Args:
        context: Airflow context
        
    Raises:
        Exception: Якщо БД недоступна
    """
    from etl.extract import OrdersExtractor, CatalogExtractor, PaymentsExtractor
    from etl.config import ETLConfig
    
    config = ETLConfig.from_env()
    
    print("Перевірка підключень до OLTP баз даних...")
    
    # Перевірка Orders DB
    try:
        orders_extractor = OrdersExtractor(config.orders_db)
        _ = orders_extractor.engine
        orders_extractor.close()
        print("✅ Orders DB: OK")
    except Exception as e:
        raise Exception(f"❌ Orders DB недоступна: {e}")
    
    # Перевірка Catalog DB
    try:
        catalog_extractor = CatalogExtractor(config.catalog_db)
        _ = catalog_extractor.engine
        catalog_extractor.close()
        print("✅ Catalog DB: OK")
    except Exception as e:
        raise Exception(f"❌ Catalog DB недоступна: {e}")
    
    # Перевірка Payments DB
    try:
        payments_extractor = PaymentsExtractor(config.payments_db)
        _ = payments_extractor.engine
        payments_extractor.close()
        print("✅ Payments DB: OK")
    except Exception as e:
        raise Exception(f"❌ Payments DB недоступна: {e}")
    
    print("Всі джерельні бази даних доступні")


def check_dwh_database(**context: Any) -> None:
    """Перевіряє доступність DWH.
    
    Args:
        context: Airflow context
        
    Raises:
        Exception: Якщо DWH недоступний
    """
    from etl.load import Loader
    from etl.config import ETLConfig
    
    config = ETLConfig.from_env()
    
    print("Перевірка підключення до DWH...")
    
    try:
        loader = Loader(config.dwh_db)
        _ = loader.engine
        loader.close()
        print("✅ DWH: OK")
    except Exception as e:
        raise Exception(f"❌ DWH недоступний: {e}")


def run_etl_full_load(**context: Any) -> dict[str, int]:
    """Виконує повне завантаження ETL.
    
    Args:
        context: Airflow context
        
    Returns:
        Статистика завантаження
    """
    from etl.config import ETLConfig
    from etl.pipeline import ETLPipeline
    
    print("=" * 60)
    print("Запуск повного ETL завантаження")
    print("=" * 60)
    
    config = ETLConfig.from_env()
    pipeline = ETLPipeline(config)
    
    results = pipeline.run_full_load()
    
    # Зберігаємо результати в XCom для наступних task
    context['task_instance'].xcom_push(key='etl_results', value=results)
    
    return results


def run_etl_incremental_load(**context: Any) -> dict[str, int]:
    """Виконує інкрементальне завантаження ETL.
    
    Args:
        context: Airflow context
        
    Returns:
        Статистика завантаження
    """
    from etl.config import ETLConfig
    from etl.pipeline import ETLPipeline
    
    # Отримуємо дати з execution_date
    execution_date = context['execution_date']
    start_date = execution_date
    end_date = execution_date + timedelta(days=1)
    
    print("=" * 60)
    print(f"Запуск інкрементального ETL завантаження")
    print(f"Період: {start_date} - {end_date}")
    print("=" * 60)
    
    config = ETLConfig.from_env()
    pipeline = ETLPipeline(config)
    
    results = pipeline.run_incremental_load(start_date, end_date)
    
    # Зберігаємо результати в XCom
    context['task_instance'].xcom_push(key='etl_results', value=results)
    
    return results


def send_success_notification(**context: Any) -> None:
    """Надсилає повідомлення про успішне завершення.
    
    Args:
        context: Airflow context
    """
    ti = context['task_instance']
    results = ti.xcom_pull(task_ids='run_etl', key='etl_results')
    
    execution_date = context['execution_date']
    
    print("=" * 60)
    print("✅ ETL процес завершено успішно!")
    print(f"Дата виконання: {execution_date}")
    print("Завантажено записів:")
    for table, count in results.items():
        print(f"  {table}: {count:,}")
    print("=" * 60)
    
    # Тут можна додати відправку email, Slack, Telegram тощо


def handle_failure(**context: Any) -> None:
    """Обробляє помилку виконання DAG.
    
    Args:
        context: Airflow context
    """
    execution_date = context['execution_date']
    task_instance = context['task_instance']
    exception = context.get('exception')
    
    print("=" * 60)
    print("❌ ETL процес завершився з помилкою!")
    print(f"Дата виконання: {execution_date}")
    print(f"Task: {task_instance.task_id}")
    print(f"Помилка: {exception}")
    print("=" * 60)
    
    # Тут можна додати відправку сповіщень про помилку


# Створення DAG для щоденного інкрементального завантаження
with DAG(
    dag_id='techmarket_etl_daily',
    default_args=DEFAULT_ARGS,
    description='Щоденне інкрементальне завантаження TechMarket ETL',
    schedule_interval='0 2 * * *',  # Щодня о 02:00 UTC
    start_date=days_ago(1),
    catchup=False,
    tags=['etl', 'techmarket', 'dwh', 'daily'],
    max_active_runs=1,
) as dag_daily:
    
    # Task 1: Перевірка джерельних БД
    check_sources = PythonOperator(
        task_id='check_source_databases',
        python_callable=check_source_databases if ETL_AVAILABLE else lambda: None,
        doc_md="Перевіряє доступність OLTP баз даних",
    )
    
    # Task 2: Перевірка DWH
    check_dwh = PythonOperator(
        task_id='check_dwh_database',
        python_callable=check_dwh_database if ETL_AVAILABLE else lambda: None,
        doc_md="Перевіряє доступність DWH",
    )
    
    # Task 3: Запуск інкрементального ETL
    run_etl = PythonOperator(
        task_id='run_etl',
        python_callable=run_etl_incremental_load if ETL_AVAILABLE else lambda: {},
        doc_md="Виконує інкрементальне завантаження даних",
    )
    
    # Task 4: Відправка повідомлення про успіх
    notify_success = PythonOperator(
        task_id='notify_success',
        python_callable=send_success_notification,
        doc_md="Надсилає повідомлення про успішне завершення",
        trigger_rule='all_success',
    )
    
    # Task 5: Обробка помилок
    notify_failure = PythonOperator(
        task_id='notify_failure',
        python_callable=handle_failure,
        doc_md="Обробляє помилки виконання",
        trigger_rule='one_failed',
    )
    
    # Визначення залежностей
    [check_sources, check_dwh] >> run_etl >> notify_success
    run_etl >> notify_failure


# DAG для щотижневого повного завантаження
with DAG(
    dag_id='techmarket_etl_weekly_full',
    default_args=DEFAULT_ARGS,
    description='Щотижневе повне завантаження TechMarket ETL',
    schedule_interval='0 3 * * 0',  # Кожної неділі о 03:00 UTC
    start_date=days_ago(1),
    catchup=False,
    tags=['etl', 'techmarket', 'dwh', 'weekly', 'full-load'],
    max_active_runs=1,
) as dag_weekly:
    
    check_sources_weekly = PythonOperator(
        task_id='check_source_databases',
        python_callable=check_source_databases if ETL_AVAILABLE else lambda: None,
    )
    
    check_dwh_weekly = PythonOperator(
        task_id='check_dwh_database',
        python_callable=check_dwh_database if ETL_AVAILABLE else lambda: None,
    )
    
    run_etl_weekly = PythonOperator(
        task_id='run_etl',
        python_callable=run_etl_full_load if ETL_AVAILABLE else lambda: {},
        execution_timeout=timedelta(hours=4),  # Більше часу для повного завантаження
    )
    
    notify_success_weekly = PythonOperator(
        task_id='notify_success',
        python_callable=send_success_notification,
        trigger_rule='all_success',
    )
    
    notify_failure_weekly = PythonOperator(
        task_id='notify_failure',
        python_callable=handle_failure,
        trigger_rule='one_failed',
    )
    
    [check_sources_weekly, check_dwh_weekly] >> run_etl_weekly >> notify_success_weekly
    run_etl_weekly >> notify_failure_weekly
