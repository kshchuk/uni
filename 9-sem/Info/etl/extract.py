"""
Extract модуль для витягування даних з OLTP баз даних.

Відповідає за підключення до MySQL баз даних та витягування необхідних даних.
"""

import logging
from typing import Optional, Generator
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .config import MySQLConfig

logger = logging.getLogger(__name__)


class Extractor:
    """Базовий клас для витягування даних з бази даних.
    
    Attributes:
        config: Конфігурація підключення до бази даних
        engine: SQLAlchemy engine для підключення
    """
    
    def __init__(self, config: MySQLConfig):
        """Ініціалізує екстрактор.
        
        Args:
            config: Конфігурація підключення до бази даних
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
                logger.info(f"З'єднання з {self.config.database} встановлено")
            except SQLAlchemyError as e:
                logger.error(f"Помилка підключення до {self.config.database}: {e}")
                raise
        return self._engine
    
    def extract_query(self, query: str, chunksize: Optional[int] = None) -> pd.DataFrame | Generator[pd.DataFrame, None, None]:
        """Виконує SQL запит та повертає результат.
        
        Args:
            query: SQL запит для виконання
            chunksize: Розмір чанку для читання великих даних (опціонально)
            
        Returns:
            DataFrame з результатами або генератор DataFrame'ів
            
        Raises:
            SQLAlchemyError: Якщо помилка виконання запиту
        """
        try:
            logger.debug(f"Виконання запиту: {query[:100]}...")
            
            if chunksize:
                return pd.read_sql(query, self.engine, chunksize=chunksize)
            else:
                return pd.read_sql(query, self.engine)
                
        except SQLAlchemyError as e:
            logger.error(f"Помилка виконання запиту: {e}")
            raise
    
    def close(self) -> None:
        """Закриває з'єднання з базою даних."""
        if self._engine:
            self._engine.dispose()
            logger.info(f"З'єднання з {self.config.database} закрито")


class OrdersExtractor(Extractor):
    """Екстрактор для Orders DB."""
    
    def extract_orders(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        chunksize: Optional[int] = None
    ) -> pd.DataFrame | Generator[pd.DataFrame, None, None]:
        """Витягує дані замовлень.
        
        Args:
            start_date: Початкова дата для фільтрації
            end_date: Кінцева дата для фільтрації
            chunksize: Розмір чанку для обробки великих даних
            
        Returns:
            DataFrame з даними замовлень або генератор DataFrame'ів
        """
        query = """
            SELECT 
                o.id as order_id,
                o.customer_id,
                o.employee_id,
                o.region_id,
                o.order_date,
                o.status,
                o.total_amount,
                o.created_at,
                oi.id as order_item_id,
                oi.product_id,
                oi.quantity,
                oi.unit_price,
                oi.discount
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status IN ('paid', 'shipped', 'delivered')
        """
        
        params = []
        if start_date:
            query += " AND o.order_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND o.order_date <= %s"
            params.append(end_date)
            
        query += " ORDER BY o.order_date, o.id"
        
        logger.info(f"Витягування замовлень з {self.config.database}")
        return self.extract_query(query, chunksize)
    
    def extract_customers(self) -> pd.DataFrame:
        """Витягує дані клієнтів.
        
        Returns:
            DataFrame з даними клієнтів
        """
        query = """
            SELECT 
                id as customer_id,
                first_name,
                last_name,
                email,
                phone,
                created_at,
                updated_at
            FROM customers
            ORDER BY created_at
        """
        
        logger.info(f"Витягування клієнтів з {self.config.database}")
        return self.extract_query(query)
    
    def extract_employees(self) -> pd.DataFrame:
        """Витягує дані співробітників.
        
        Returns:
            DataFrame з даними співробітників
        """
        query = """
            SELECT 
                e.id as employee_id,
                e.first_name,
                e.last_name,
                e.email,
                e.phone,
                e.is_manager,
                e.region_id,
                r.name as region_name,
                e.created_at
            FROM employees e
            LEFT JOIN regions r ON e.region_id = r.id
            ORDER BY e.created_at
        """
        
        logger.info(f"Витягування співробітників з {self.config.database}")
        return self.extract_query(query)
    
    def extract_regions(self) -> pd.DataFrame:
        """Витягує дані регіонів.
        
        Returns:
            DataFrame з даними регіонів
        """
        query = """
            SELECT 
                id as region_id,
                name as region_name,
                code as region_code
            FROM regions
            ORDER BY name
        """
        
        logger.info(f"Витягування регіонів з {self.config.database}")
        return self.extract_query(query)


class CatalogExtractor(Extractor):
    """Екстрактор для Catalog DB."""
    
    def extract_products(self) -> pd.DataFrame:
        """Витягує дані товарів.
        
        Returns:
            DataFrame з даними товарів
        """
        query = """
            SELECT 
                p.id as product_id,
                p.name as product_name,
                p.description,
                p.price,
                p.stock_quantity,
                p.category_id,
                c.name as category_name,
                c.parent_category_id,
                p.created_at,
                p.updated_at
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.created_at
        """
        
        logger.info(f"Витягування товарів з {self.config.database}")
        return self.extract_query(query)
    
    def extract_categories(self) -> pd.DataFrame:
        """Витягує дані категорій.
        
        Returns:
            DataFrame з даними категорій
        """
        query = """
            SELECT 
                id as category_id,
                name as category_name,
                parent_category_id,
                created_at
            FROM categories
            ORDER BY parent_category_id IS NULL DESC, parent_category_id, name
        """
        
        logger.info(f"Витягування категорій з {self.config.database}")
        return self.extract_query(query)


class PaymentsExtractor(Extractor):
    """Екстрактор для Payments DB."""
    
    def extract_payments(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Витягує дані платежів.
        
        Args:
            start_date: Початкова дата для фільтрації
            end_date: Кінцева дата для фільтрації
            
        Returns:
            DataFrame з даними платежів
        """
        query = """
            SELECT 
                id as payment_id,
                order_id,
                amount,
                payment_method,
                payment_date,
                status as payment_status,
                transaction_id,
                created_at
            FROM payments
            WHERE status = 'completed'
        """
        
        params = []
        if start_date:
            query += " AND payment_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND payment_date <= %s"
            params.append(end_date)
            
        query += " ORDER BY payment_date"
        
        logger.info(f"Витягування платежів з {self.config.database}")
        return self.extract_query(query)
