"""
Transform модуль для очищення та трансформації даних.

Відповідає за:
- Видалення дублікатів
- Обробку пропущених значень
- Агрегацію даних
- Підготовку даних для завантаження в DWH
"""

import logging
from typing import Optional
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataCleaner:
    """Клас для очищення даних."""
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: Optional[list[str]] = None) -> pd.DataFrame:
        """Видаляє дублікати з DataFrame.
        
        Args:
            df: Вхідний DataFrame
            subset: Список колонок для перевірки на дублікати
            
        Returns:
            DataFrame без дублікатів
        """
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep='first')
        removed_count = initial_count - len(df_clean)
        
        if removed_count > 0:
            logger.info(f"Видалено {removed_count} дублікатів")
        
        return df_clean
    
    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame,
        strategy: str = 'drop',
        fill_value: Optional[dict[str, any]] = None
    ) -> pd.DataFrame:
        """Обробляє пропущені значення.
        
        Args:
            df: Вхідний DataFrame
            strategy: Стратегія обробки ('drop', 'fill', 'forward_fill')
            fill_value: Словник значень для заповнення (колонка: значення)
            
        Returns:
            DataFrame з обробленими пропущеними значеннями
        """
        missing_count = df.isnull().sum().sum()
        
        if missing_count == 0:
            logger.info("Пропущені значення відсутні")
            return df
        
        logger.info(f"Знайдено {missing_count} пропущених значень")
        
        if strategy == 'drop':
            df_clean = df.dropna()
            logger.info(f"Видалено {len(df) - len(df_clean)} рядків з пропущеними значеннями")
        elif strategy == 'fill' and fill_value:
            df_clean = df.fillna(fill_value)
            logger.info("Пропущені значення заповнено вказаними значеннями")
        elif strategy == 'forward_fill':
            df_clean = df.fillna(method='ffill')
            logger.info("Пропущені значення заповнено попередніми значеннями")
        else:
            logger.warning(f"Невідома стратегія: {strategy}. Дані не змінено")
            df_clean = df
        
        return df_clean
    
    @staticmethod
    def validate_data_types(df: pd.DataFrame, schema: dict[str, str]) -> pd.DataFrame:
        """Валідує та приводить типи даних до потрібного формату.
        
        Args:
            df: Вхідний DataFrame
            schema: Словник з описом типів (колонка: тип)
            
        Returns:
            DataFrame з валідованими типами
        """
        df_validated = df.copy()
        
        for column, dtype in schema.items():
            if column in df_validated.columns:
                try:
                    if dtype == 'datetime':
                        df_validated[column] = pd.to_datetime(df_validated[column])
                    elif dtype == 'numeric':
                        df_validated[column] = pd.to_numeric(df_validated[column])
                    else:
                        df_validated[column] = df_validated[column].astype(dtype)
                    logger.debug(f"Колонка {column} приведена до типу {dtype}")
                except Exception as e:
                    logger.error(f"Помилка приведення типу для {column}: {e}")
                    raise
        
        return df_validated


class DataTransformer:
    """Клас для трансформації та агрегації даних."""
    
    def __init__(self):
        """Ініціалізує трансформер."""
        self.cleaner = DataCleaner()
    
    def transform_orders(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """Трансформує дані замовлень для DWH.
        
        Args:
            orders_df: DataFrame з витягнутими замовленнями
            
        Returns:
            Трансформований DataFrame
        """
        logger.info("Трансформація даних замовлень")
        
        # Видаляємо дублікати
        orders_df = self.cleaner.remove_duplicates(
            orders_df,
            subset=['order_id', 'order_item_id']
        )
        
        # Валідуємо типи даних
        schema = {
            'order_date': 'datetime',
            'created_at': 'datetime',
            'quantity': 'int',
            'unit_price': 'float',
            'discount': 'float',
            'total_amount': 'float'
        }
        orders_df = self.cleaner.validate_data_types(orders_df, schema)
        
        # Обчислюємо додаткові поля
        orders_df['revenue'] = orders_df['unit_price'] * orders_df['quantity']
        orders_df['discount_amount'] = orders_df['discount'].fillna(0)
        orders_df['cost'] = orders_df['revenue'] * 0.6  # Припускаємо 60% собівартість
        orders_df['margin'] = orders_df['revenue'] - orders_df['discount_amount'] - orders_df['cost']
        
        # Додаємо date_key для зв'язку з dim_date
        orders_df['date_key'] = orders_df['order_date'].dt.strftime('%Y%m%d').astype(int)
        
        logger.info(f"Трансформовано {len(orders_df)} записів замовлень")
        return orders_df
    
    def transform_customers(self, customers_df: pd.DataFrame) -> pd.DataFrame:
        """Трансформує дані клієнтів для DWH.
        
        Args:
            customers_df: DataFrame з витягнутими клієнтами
            
        Returns:
            Трансформований DataFrame
        """
        logger.info("Трансформація даних клієнтів")
        
        # Видаляємо дублікати по email
        customers_df = self.cleaner.remove_duplicates(
            customers_df,
            subset=['email']
        )
        
        # Об'єднуємо ім'я та прізвище
        customers_df['full_name'] = (
            customers_df['first_name'].fillna('') + ' ' + 
            customers_df['last_name'].fillna('')
        ).str.strip()
        
        # Очищуємо email (нижній регістр)
        customers_df['email'] = customers_df['email'].str.lower().str.strip()
        
        # Валідуємо типи
        schema = {
            'created_at': 'datetime',
            'updated_at': 'datetime'
        }
        customers_df = self.cleaner.validate_data_types(customers_df, schema)
        
        logger.info(f"Трансформовано {len(customers_df)} клієнтів")
        return customers_df
    
    def transform_products(self, products_df: pd.DataFrame) -> pd.DataFrame:
        """Трансформує дані товарів для DWH.
        
        Args:
            products_df: DataFrame з витягнутими товарами
            
        Returns:
            Трансформований DataFrame
        """
        logger.info("Трансформація даних товарів")
        
        # Видаляємо дублікати
        products_df = self.cleaner.remove_duplicates(
            products_df,
            subset=['product_id']
        )
        
        # Обробляємо пропущені значення
        products_df = self.cleaner.handle_missing_values(
            products_df,
            strategy='fill',
            fill_value={
                'description': 'Опис відсутній',
                'stock_quantity': 0,
                'category_name': 'Без категорії'
            }
        )
        
        # Валідуємо типи
        schema = {
            'price': 'float',
            'stock_quantity': 'int',
            'created_at': 'datetime',
            'updated_at': 'datetime'
        }
        products_df = self.cleaner.validate_data_types(products_df, schema)
        
        logger.info(f"Трансформовано {len(products_df)} товарів")
        return products_df
    
    def aggregate_sales_by_period(
        self,
        orders_df: pd.DataFrame,
        period: str = 'D'
    ) -> pd.DataFrame:
        """Агрегує продажі за період.
        
        Args:
            orders_df: DataFrame з замовленнями
            period: Період агрегації ('D'-день, 'W'-тиждень, 'M'-місяць)
            
        Returns:
            Агрегований DataFrame
        """
        logger.info(f"Агрегація продажів за період: {period}")
        
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        
        agg_df = orders_df.groupby(pd.Grouper(key='order_date', freq=period)).agg({
            'order_id': 'nunique',
            'quantity': 'sum',
            'revenue': 'sum',
            'discount_amount': 'sum',
            'margin': 'sum'
        }).reset_index()
        
        agg_df.columns = [
            'period_date',
            'orders_count',
            'total_quantity',
            'total_revenue',
            'total_discount',
            'total_margin'
        ]
        
        logger.info(f"Створено {len(agg_df)} агрегованих записів")
        return agg_df
    
    def aggregate_sales_by_product(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """Агрегує продажі за товаром.
        
        Args:
            orders_df: DataFrame з замовленнями
            
        Returns:
            Агрегований DataFrame з топ товарами
        """
        logger.info("Агрегація продажів за товаром")
        
        agg_df = orders_df.groupby('product_id').agg({
            'order_id': 'nunique',
            'quantity': 'sum',
            'revenue': 'sum',
            'margin': 'sum'
        }).reset_index()
        
        agg_df.columns = [
            'product_id',
            'orders_count',
            'total_quantity',
            'total_revenue',
            'total_margin'
        ]
        
        # Сортуємо за виручкою
        agg_df = agg_df.sort_values('total_revenue', ascending=False)
        
        logger.info(f"Агреговано дані для {len(agg_df)} товарів")
        return agg_df
    
    def aggregate_sales_by_employee(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """Агрегує продажі за співробітником.
        
        Args:
            orders_df: DataFrame з замовленнями
            
        Returns:
            Агрегований DataFrame з результатами співробітників
        """
        logger.info("Агрегація продажів за співробітником")
        
        agg_df = orders_df.groupby('employee_id').agg({
            'order_id': 'nunique',
            'quantity': 'sum',
            'revenue': 'sum',
            'margin': 'sum'
        }).reset_index()
        
        agg_df.columns = [
            'employee_id',
            'orders_count',
            'total_quantity',
            'total_revenue',
            'total_margin'
        ]
        
        # Обчислюємо середній чек
        agg_df['avg_order_value'] = agg_df['total_revenue'] / agg_df['orders_count']
        
        # Сортуємо за виручкою
        agg_df = agg_df.sort_values('total_revenue', ascending=False)
        
        logger.info(f"Агреговано дані для {len(agg_df)} співробітників")
        return agg_df
