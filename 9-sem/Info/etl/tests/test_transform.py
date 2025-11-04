"""
Тести для Transform модуля.

Перевіряє коректність очищення та трансформації даних.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from etl.transform import DataCleaner, DataTransformer


@pytest.fixture
def sample_df_with_duplicates():
    """Фікстура з дублікатами."""
    return pd.DataFrame({
        'id': ['1', '2', '2', '3'],
        'name': ['A', 'B', 'B', 'C'],
        'value': [10, 20, 20, 30]
    })


@pytest.fixture
def sample_df_with_missing():
    """Фікстура з пропущеними значеннями."""
    return pd.DataFrame({
        'id': ['1', '2', '3', '4'],
        'name': ['A', 'B', None, 'D'],
        'value': [10, None, 30, 40]
    })


@pytest.fixture
def sample_orders_df():
    """Фікстура з замовленнями."""
    return pd.DataFrame({
        'order_id': ['order1', 'order2'],
        'order_item_id': ['item1', 'item2'],
        'order_date': pd.to_datetime(['2024-01-01', '2024-01-02']),
        'created_at': pd.to_datetime(['2024-01-01 10:00:00', '2024-01-02 11:00:00']),
        'quantity': [2, 3],
        'unit_price': [100.0, 150.0],
        'discount': [10.0, 0.0],
        'total_amount': [190.0, 450.0],
        'customer_id': ['cust1', 'cust2'],
        'employee_id': ['emp1', 'emp2'],
        'region_id': ['reg1', 'reg2'],
        'product_id': ['prod1', 'prod2']
    })


@pytest.fixture
def sample_customers_df():
    """Фікстура з клієнтами."""
    return pd.DataFrame({
        'customer_id': ['cust1', 'cust2'],
        'first_name': ['John', 'Jane'],
        'last_name': ['Doe', 'Smith'],
        'email': ['JOHN@EXAMPLE.COM', 'jane@example.com'],
        'created_at': pd.to_datetime(['2024-01-01', '2024-01-02']),
        'updated_at': pd.to_datetime(['2024-01-01', '2024-01-02'])
    })


@pytest.fixture
def sample_products_df():
    """Фікстура з товарами."""
    return pd.DataFrame({
        'product_id': ['prod1', 'prod2', 'prod3'],
        'product_name': ['Product 1', 'Product 2', 'Product 3'],
        'description': ['Desc 1', None, 'Desc 3'],
        'price': [100.0, 200.0, 300.0],
        'stock_quantity': [10, None, 30],
        'category_id': ['cat1', 'cat2', None],
        'category_name': ['Category 1', 'Category 2', None],
        'created_at': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
        'updated_at': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
    })


class TestDataCleaner:
    """Тести для DataCleaner."""
    
    def test_remove_duplicates(self, sample_df_with_duplicates):
        """Тест видалення дублікатів."""
        cleaner = DataCleaner()
        result = cleaner.remove_duplicates(sample_df_with_duplicates, subset=['id'])
        
        assert len(result) == 3
        assert result['id'].tolist() == ['1', '2', '3']
    
    def test_remove_duplicates_keep_first(self, sample_df_with_duplicates):
        """Тест що залишається перший запис при дублікаті."""
        cleaner = DataCleaner()
        result = cleaner.remove_duplicates(sample_df_with_duplicates, subset=['id', 'name'])
        
        assert len(result) == 3
        # Перевіряємо що перший дублікат залишився
        duplicate_rows = result[result['id'] == '2']
        assert len(duplicate_rows) == 1
    
    def test_handle_missing_values_drop(self, sample_df_with_missing):
        """Тест видалення рядків з пропущеними значеннями."""
        cleaner = DataCleaner()
        result = cleaner.handle_missing_values(sample_df_with_missing, strategy='drop')
        
        assert len(result) == 2
        assert result['name'].isna().sum() == 0
        assert result['value'].isna().sum() == 0
    
    def test_handle_missing_values_fill(self, sample_df_with_missing):
        """Тест заповнення пропущених значень."""
        cleaner = DataCleaner()
        fill_values = {'name': 'Unknown', 'value': 0}
        result = cleaner.handle_missing_values(
            sample_df_with_missing,
            strategy='fill',
            fill_value=fill_values
        )
        
        assert len(result) == 4
        assert result['name'].isna().sum() == 0
        assert result['value'].isna().sum() == 0
        assert 'Unknown' in result['name'].values
    
    def test_handle_missing_values_no_missing(self):
        """Тест коли пропущені значення відсутні."""
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        cleaner = DataCleaner()
        result = cleaner.handle_missing_values(df, strategy='drop')
        
        assert len(result) == 3
        pd.testing.assert_frame_equal(df, result)
    
    def test_validate_data_types(self):
        """Тест валідації типів даних."""
        df = pd.DataFrame({
            'date_col': ['2024-01-01', '2024-01-02'],
            'num_col': ['10', '20'],
            'str_col': ['A', 'B']
        })
        
        schema = {
            'date_col': 'datetime',
            'num_col': 'numeric',
            'str_col': 'str'
        }
        
        cleaner = DataCleaner()
        result = cleaner.validate_data_types(df, schema)
        
        assert pd.api.types.is_datetime64_any_dtype(result['date_col'])
        assert pd.api.types.is_numeric_dtype(result['num_col'])
        assert pd.api.types.is_string_dtype(result['str_col'])


class TestDataTransformer:
    """Тести для DataTransformer."""
    
    def test_transform_orders(self, sample_orders_df):
        """Тест трансформації замовлень."""
        transformer = DataTransformer()
        result = transformer.transform_orders(sample_orders_df)
        
        # Перевіряємо наявність нових колонок
        assert 'revenue' in result.columns
        assert 'discount_amount' in result.columns
        assert 'cost' in result.columns
        assert 'margin' in result.columns
        assert 'date_key' in result.columns
        
        # Перевіряємо обчислення
        assert result.loc[0, 'revenue'] == 200.0  # 2 * 100
        assert result.loc[1, 'revenue'] == 450.0  # 3 * 150
        
        # Перевіряємо date_key
        assert result.loc[0, 'date_key'] == 20240101
        assert result.loc[1, 'date_key'] == 20240102
    
    def test_transform_orders_removes_duplicates(self):
        """Тест що трансформація видаляє дублікати."""
        df_with_dupes = pd.DataFrame({
            'order_id': ['order1', 'order1'],
            'order_item_id': ['item1', 'item1'],
            'order_date': pd.to_datetime(['2024-01-01', '2024-01-01']),
            'created_at': pd.to_datetime(['2024-01-01', '2024-01-01']),
            'quantity': [2, 2],
            'unit_price': [100.0, 100.0],
            'discount': [0.0, 0.0],
            'total_amount': [200.0, 200.0],
            'customer_id': ['cust1', 'cust1'],
            'employee_id': ['emp1', 'emp1'],
            'region_id': ['reg1', 'reg1'],
            'product_id': ['prod1', 'prod1']
        })
        
        transformer = DataTransformer()
        result = transformer.transform_orders(df_with_dupes)
        
        assert len(result) == 1
    
    def test_transform_customers(self, sample_customers_df):
        """Тест трансформації клієнтів."""
        transformer = DataTransformer()
        result = transformer.transform_customers(sample_customers_df)
        
        # Перевіряємо full_name
        assert 'full_name' in result.columns
        assert result.loc[0, 'full_name'] == 'John Doe'
        assert result.loc[1, 'full_name'] == 'Jane Smith'
        
        # Перевіряємо нормалізацію email
        assert result['email'].str.islower().all()
        assert result.loc[0, 'email'] == 'john@example.com'
    
    def test_transform_customers_removes_email_duplicates(self):
        """Тест що видаляються дублікати по email."""
        df_with_dupes = pd.DataFrame({
            'customer_id': ['cust1', 'cust2'],
            'first_name': ['John', 'Jane'],
            'last_name': ['Doe', 'Doe'],
            'email': ['john@example.com', 'john@example.com'],
            'created_at': pd.to_datetime(['2024-01-01', '2024-01-02']),
            'updated_at': pd.to_datetime(['2024-01-01', '2024-01-02'])
        })
        
        transformer = DataTransformer()
        result = transformer.transform_customers(df_with_dupes)
        
        assert len(result) == 1
    
    def test_transform_products(self, sample_products_df):
        """Тест трансформації товарів."""
        transformer = DataTransformer()
        result = transformer.transform_products(sample_products_df)
        
        # Перевіряємо що пропущені значення заповнені
        assert result['description'].isna().sum() == 0
        assert result['stock_quantity'].isna().sum() == 0
        assert result['category_name'].isna().sum() == 0
        
        # Перевіряємо значення за замовчуванням
        assert 'Опис відсутній' in result['description'].values
        assert 'Без категорії' in result['category_name'].values
    
    def test_aggregate_sales_by_period(self, sample_orders_df):
        """Тест агрегації продажів за період."""
        # Додаємо необхідні колонки
        sample_orders_df['revenue'] = sample_orders_df['unit_price'] * sample_orders_df['quantity']
        sample_orders_df['discount_amount'] = sample_orders_df['discount']
        sample_orders_df['margin'] = sample_orders_df['revenue'] - sample_orders_df['discount_amount']
        
        transformer = DataTransformer()
        result = transformer.aggregate_sales_by_period(sample_orders_df, period='D')
        
        # Перевіряємо колонки
        assert 'period_date' in result.columns
        assert 'orders_count' in result.columns
        assert 'total_quantity' in result.columns
        assert 'total_revenue' in result.columns
        
        # Перевіряємо дані
        assert len(result) == 2  # 2 дні
        assert result['orders_count'].sum() == 2
        assert result['total_quantity'].sum() == 5  # 2 + 3
    
    def test_aggregate_sales_by_product(self, sample_orders_df):
        """Тест агрегації продажів за товаром."""
        # Додаємо необхідні колонки
        sample_orders_df['revenue'] = sample_orders_df['unit_price'] * sample_orders_df['quantity']
        sample_orders_df['margin'] = sample_orders_df['revenue'] * 0.4
        
        transformer = DataTransformer()
        result = transformer.aggregate_sales_by_product(sample_orders_df)
        
        # Перевіряємо колонки
        assert 'product_id' in result.columns
        assert 'orders_count' in result.columns
        assert 'total_quantity' in result.columns
        assert 'total_revenue' in result.columns
        
        # Перевіряємо що дані відсортовані за виручкою
        assert result['total_revenue'].is_monotonic_decreasing
        
        assert len(result) == 2
    
    def test_aggregate_sales_by_employee(self, sample_orders_df):
        """Тест агрегації продажів за співробітником."""
        # Додаємо необхідні колонки
        sample_orders_df['revenue'] = sample_orders_df['unit_price'] * sample_orders_df['quantity']
        sample_orders_df['margin'] = sample_orders_df['revenue'] * 0.4
        
        transformer = DataTransformer()
        result = transformer.aggregate_sales_by_employee(sample_orders_df)
        
        # Перевіряємо колонки
        assert 'employee_id' in result.columns
        assert 'orders_count' in result.columns
        assert 'avg_order_value' in result.columns
        
        # Перевіряємо обчислення середнього чеку
        assert result.loc[0, 'avg_order_value'] == result.loc[0, 'total_revenue'] / result.loc[0, 'orders_count']
        
        # Перевіряємо що дані відсортовані за виручкою
        assert result['total_revenue'].is_monotonic_decreasing
