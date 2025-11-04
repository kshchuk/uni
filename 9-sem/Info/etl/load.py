"""
Load модуль для завантаження даних у DWH.

Відповідає за завантаження трансформованих даних у PostgreSQL DWH.
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .config import PostgreSQLConfig

logger = logging.getLogger(__name__)


class Loader:
    """Клас для завантаження даних у DWH.
    
    Attributes:
        config: Конфігурація підключення до DWH
        engine: SQLAlchemy engine для підключення
    """
    
    def __init__(self, config: PostgreSQLConfig):
        """Ініціалізує лоадер.
        
        Args:
            config: Конфігурація підключення до PostgreSQL DWH
        """
        self.config = config
        self._engine: Optional[Engine] = None
        
    @property
    def engine(self) -> Engine:
        """Повертає SQLAlchemy engine, створюючи його при потребі.
        
        Returns:
            SQLAlchemy Engine об'єкт
            
        Raises:
            SQLAlchemyError: Якщо не вдалося створити з'єднання
        """
        if self._engine is None:
            try:
                self._engine = create_engine(
                    self.config.connection_string,
                    pool_pre_ping=True,
                    pool_recycle=3600
                )
                logger.info(f"З'єднання з DWH ({self.config.database}) встановлено")
            except SQLAlchemyError as e:
                logger.error(f"Помилка підключення до DWH: {e}")
                raise
        return self._engine
    
    def load_dimension(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = 'append'
    ) -> int:
        """Завантажує дані в таблицю-вимір.
        
        Args:
            df: DataFrame для завантаження
            table_name: Назва таблиці в DWH
            if_exists: Дія при існуванні таблиці ('append', 'replace', 'fail')
            
        Returns:
            Кількість завантажених записів
            
        Raises:
            SQLAlchemyError: Якщо помилка завантаження
        """
        try:
            logger.info(f"Завантаження {len(df)} записів у {table_name}")
            
            rows_inserted = df.to_sql(
                table_name,
                self.engine,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=1000
            )
            
            logger.info(f"Успішно завантажено {len(df)} записів у {table_name}")
            return len(df)
            
        except SQLAlchemyError as e:
            logger.error(f"Помилка завантаження в {table_name}: {e}")
            raise
    
    def load_fact_sales(self, df: pd.DataFrame, if_exists: str = 'append') -> int:
        """Завантажує дані продажів у fact_sales.
        
        Args:
            df: DataFrame з фактами продажів
            if_exists: Дія при існуванні таблиці
            
        Returns:
            Кількість завантажених записів
        """
        logger.info(f"Завантаження фактів продажів: {len(df)} записів")
        
        # Переконуємося що всі необхідні колонки присутні
        required_columns = [
            'order_id', 'order_item_id', 'date_key', 'product_id',
            'customer_id', 'employee_id', 'region_id', 'quantity',
            'revenue', 'discount_amount', 'cost', 'margin'
        ]
        
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Відсутні необхідні колонки: {missing_columns}")
        
        return self.load_dimension(df[required_columns], 'fact_sales', if_exists)
    
    def truncate_table(self, table_name: str) -> None:
        """Очищає таблицю в DWH.
        
        Args:
            table_name: Назва таблиці для очищення
            
        Raises:
            SQLAlchemyError: Якщо помилка очищення
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
                conn.commit()
            logger.info(f"Таблиця {table_name} очищена")
        except SQLAlchemyError as e:
            logger.error(f"Помилка очищення {table_name}: {e}")
            raise
    
    def load_dim_date(self, start_date: datetime, end_date: datetime) -> int:
        """Завантажує дані у таблицю dim_date.
        
        Args:
            start_date: Початкова дата
            end_date: Кінцева дата
            
        Returns:
            Кількість завантажених записів
        """
        logger.info(f"Генерація dim_date з {start_date} до {end_date}")
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        date_data = []
        for date in dates:
            date_data.append({
                'date_key': int(date.strftime('%Y%m%d')),
                'date': date,
                'year': date.year,
                'quarter': date.quarter,
                'month': date.month,
                'month_name': date.strftime('%B'),
                'day': date.day,
                'day_of_week': date.dayofweek + 1,
                'day_name': date.strftime('%A'),
                'week_of_year': date.isocalendar()[1],
                'is_weekend': date.dayofweek >= 5
            })
        
        df_date = pd.DataFrame(date_data)
        return self.load_dimension(df_date, 'dim_date', if_exists='replace')
    
    def get_existing_keys(self, table_name: str, key_column: str) -> set[str]:
        """Отримує існуючі ключі з таблиці-виміру.
        
        Args:
            table_name: Назва таблиці
            key_column: Назва колонки з ключем
            
        Returns:
            Множина існуючих ключів
        """
        try:
            query = f"SELECT {key_column} FROM {table_name}"
            df = pd.read_sql(query, self.engine)
            return set(df[key_column].values)
        except SQLAlchemyError as e:
            logger.error(f"Помилка отримання ключів з {table_name}: {e}")
            return set()
    
    def upsert_dimension(
        self,
        df: pd.DataFrame,
        table_name: str,
        key_column: str
    ) -> dict[str, int]:
        """Виконує upsert (insert or update) для таблиці-виміру.
        
        Args:
            df: DataFrame для завантаження
            table_name: Назва таблиці
            key_column: Колонка-ключ для перевірки існування
            
        Returns:
            Словник з кількістю вставлених та оновлених записів
        """
        logger.info(f"Upsert в {table_name}: {len(df)} записів")
        
        existing_keys = self.get_existing_keys(table_name, key_column)
        
        # Розділяємо на нові та існуючі
        df_new = df[~df[key_column].isin(existing_keys)]
        df_existing = df[df[key_column].isin(existing_keys)]
        
        inserted = 0
        updated = 0
        
        # Вставляємо нові
        if len(df_new) > 0:
            inserted = self.load_dimension(df_new, table_name, if_exists='append')
        
        # Оновлюємо існуючі (видаляємо та вставляємо знову)
        if len(df_existing) > 0:
            try:
                with self.engine.connect() as conn:
                    for _, row in df_existing.iterrows():
                        # Видаляємо старий запис
                        delete_query = text(f"DELETE FROM {table_name} WHERE {key_column} = :key")
                        conn.execute(delete_query, {"key": row[key_column]})
                    conn.commit()
                
                # Вставляємо оновлені
                updated = self.load_dimension(df_existing, table_name, if_exists='append')
                
            except SQLAlchemyError as e:
                logger.error(f"Помилка оновлення в {table_name}: {e}")
                raise
        
        logger.info(f"Upsert завершено: вставлено {inserted}, оновлено {updated}")
        return {"inserted": inserted, "updated": updated}
    
    def close(self) -> None:
        """Закриває з'єднання з DWH."""
        if self._engine:
            self._engine.dispose()
            logger.info("З'єднання з DWH закрито")
