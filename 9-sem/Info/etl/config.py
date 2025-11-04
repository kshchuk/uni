"""
Конфігурація ETL процесу.

Містить налаштування підключення до баз даних та параметри ETL.
"""

from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    """Конфігурація підключення до бази даних.
    
    Attributes:
        host: Адреса хосту бази даних
        port: Порт бази даних
        user: Ім'я користувача
        password: Пароль користувача
        database: Назва бази даних
    """
    host: str
    port: int
    user: str
    password: str
    database: str
    
    @property
    def connection_string(self) -> str:
        """Генерує рядок підключення для SQLAlchemy.
        
        Returns:
            Рядок підключення у форматі SQLAlchemy
        """
        raise NotImplementedError("Має бути реалізовано в підкласі")


@dataclass
class MySQLConfig(DatabaseConfig):
    """Конфігурація для MySQL бази даних."""
    
    @property
    def connection_string(self) -> str:
        """Генерує рядок підключення для MySQL.
        
        Returns:
            Рядок підключення: mysql+pymysql://user:pass@host:port/db
        """
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class PostgreSQLConfig(DatabaseConfig):
    """Конфігурація для PostgreSQL бази даних."""
    
    @property
    def connection_string(self) -> str:
        """Генерує рядок підключення для PostgreSQL.
        
        Returns:
            Рядок підключення: postgresql+psycopg2://user:pass@host:port/db
        """
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class ETLConfig:
    """Конфігурація ETL процесу.
    
    Attributes:
        auth_db: Конфігурація Auth DB (MySQL)
        catalog_db: Конфігурація Catalog DB (MySQL)
        orders_db: Конфігурація Orders DB (MySQL)
        payments_db: Конфігурація Payments DB (MySQL)
        dwh_db: Конфігурація DWH DB (PostgreSQL)
        batch_size: Розмір пакету для обробки даних
        incremental: Чи використовувати інкрементальне завантаження
        log_level: Рівень логування
    """
    auth_db: MySQLConfig
    catalog_db: MySQLConfig
    orders_db: MySQLConfig
    payments_db: MySQLConfig
    dwh_db: PostgreSQLConfig
    batch_size: int = 1000
    incremental: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "ETLConfig":
        """Створює конфігурацію з змінних оточення.
        
        Returns:
            Об'єкт ETLConfig з налаштуваннями
        """
        auth_db = MySQLConfig(
            host=os.getenv("AUTH_DB_HOST", "localhost"),
            port=int(os.getenv("AUTH_DB_PORT", "3306")),
            user=os.getenv("AUTH_DB_USER", "auth_user"),
            password=os.getenv("AUTH_DB_PASSWORD", "auth_pass"),
            database=os.getenv("AUTH_DB_NAME", "auth_db")
        )
        
        catalog_db = MySQLConfig(
            host=os.getenv("CATALOG_DB_HOST", "localhost"),
            port=int(os.getenv("CATALOG_DB_PORT", "3307")),
            user=os.getenv("CATALOG_DB_USER", "catalog_user"),
            password=os.getenv("CATALOG_DB_PASSWORD", "catalog_pass"),
            database=os.getenv("CATALOG_DB_NAME", "catalog_db")
        )
        
        orders_db = MySQLConfig(
            host=os.getenv("ORDERS_DB_HOST", "localhost"),
            port=int(os.getenv("ORDERS_DB_PORT", "3308")),
            user=os.getenv("ORDERS_DB_USER", "orders_user"),
            password=os.getenv("ORDERS_DB_PASSWORD", "orders_pass"),
            database=os.getenv("ORDERS_DB_NAME", "orders_db")
        )
        
        payments_db = MySQLConfig(
            host=os.getenv("PAYMENTS_DB_HOST", "localhost"),
            port=int(os.getenv("PAYMENTS_DB_PORT", "3309")),
            user=os.getenv("PAYMENTS_DB_USER", "payments_user"),
            password=os.getenv("PAYMENTS_DB_PASSWORD", "payments_pass"),
            database=os.getenv("PAYMENTS_DB_NAME", "payments_db")
        )
        
        dwh_db = PostgreSQLConfig(
            host=os.getenv("DWH_DB_HOST", "localhost"),
            port=int(os.getenv("DWH_DB_PORT", "5432")),
            user=os.getenv("DWH_DB_USER", "dwh_user"),
            password=os.getenv("DWH_DB_PASSWORD", "dwh_pass"),
            database=os.getenv("DWH_DB_NAME", "dwh_db")
        )
        
        return cls(
            auth_db=auth_db,
            catalog_db=catalog_db,
            orders_db=orders_db,
            payments_db=payments_db,
            dwh_db=dwh_db,
            batch_size=int(os.getenv("ETL_BATCH_SIZE", "1000")),
            incremental=os.getenv("ETL_INCREMENTAL", "false").lower() == "true",
            log_level=os.getenv("ETL_LOG_LEVEL", "INFO")
        )
