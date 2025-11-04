# Dockerfile для Apache Airflow з TechMarket ETL
FROM apache/airflow:2.7.3-python3.12

USER root

# Встановлення системних залежностей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        default-mysql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

# Копіювання requirements для ETL
COPY etl/requirements.txt /tmp/etl-requirements.txt

# Встановлення Python залежностей для ETL
RUN pip install --no-cache-dir -r /tmp/etl-requirements.txt

# Встановлення додаткових Airflow провайдерів
RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres==5.7.1 \
    apache-airflow-providers-mysql==5.4.0 \
    apache-airflow-providers-slack==8.4.0 \
    apache-airflow-providers-email==1.3.0

# Копіювання ETL пакету
COPY --chown=airflow:root etl /opt/airflow/etl

# Встановлення ETL пакету
RUN pip install -e /opt/airflow/etl

WORKDIR /opt/airflow
