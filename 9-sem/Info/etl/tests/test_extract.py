"""
Тести для Extract модуля.

Перевіряє коректність витягування даних з баз даних.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from etl.config import MySQLConfig
from etl.extract import Extractor, OrdersExtractor, CatalogExtractor, PaymentsExtractor


@pytest.fixture
def mysql_config():
    """Фікстура для MySQL конфігурації."""
    return MySQLConfig(
        host="localhost",
        port=3306,
        user="test_user",
        password="test_pass",
        database="test_db"
    )


@pytest.fixture
def sample_orders_df():
    """Фікстура з прикладом даних замовлень."""
    return pd.DataFrame({
        'order_id': ['order1', 'order2'],
        'customer_id': ['cust1', 'cust2'],
        'employee_id': ['emp1', 'emp2'],
        'region_id': ['reg1', 'reg2'],
        'order_date': pd.to_datetime(['2024-01-01', '2024-01-02']),
        'status': ['paid', 'shipped'],
        'total_amount': [100.0, 200.0],
        'order_item_id': ['item1', 'item2'],
        'product_id': ['prod1', 'prod2'],
        'quantity': [1, 2],
        'unit_price': [100.0, 100.0],
        'discount': [0.0, 10.0]
    })


class TestExtractor:
    """Тести для базового класу Extractor."""
    
    def test_init(self, mysql_config):
        """Тест ініціалізації екстрактора."""
        extractor = Extractor(mysql_config)
        assert extractor.config == mysql_config
        assert extractor._engine is None
    
    def test_connection_string_property(self, mysql_config):
        """Тест генерації connection string."""
        expected = "mysql+pymysql://test_user:test_pass@localhost:3306/test_db"
        assert mysql_config.connection_string == expected
    
    @patch('etl.extract.create_engine')
    def test_engine_property_creates_engine(self, mock_create_engine, mysql_config):
        """Тест створення engine при першому доступі."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        extractor = Extractor(mysql_config)
        engine = extractor.engine
        
        assert engine == mock_engine
        mock_create_engine.assert_called_once()
    
    @patch('etl.extract.create_engine')
    @patch('etl.extract.pd.read_sql')
    def test_extract_query_success(
        self,
        mock_read_sql,
        mock_create_engine,
        mysql_config,
        sample_orders_df
    ):
        """Тест успішного виконання запиту."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_read_sql.return_value = sample_orders_df
        
        extractor = Extractor(mysql_config)
        result = extractor.extract_query("SELECT * FROM test")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        mock_read_sql.assert_called_once()
    
    @patch('etl.extract.create_engine')
    def test_close_disposes_engine(self, mock_create_engine, mysql_config):
        """Тест закриття з'єднання."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        extractor = Extractor(mysql_config)
        _ = extractor.engine  # Створюємо engine
        extractor.close()
        
        mock_engine.dispose.assert_called_once()


class TestOrdersExtractor:
    """Тести для OrdersExtractor."""
    
    @patch('etl.extract.Extractor.extract_query')
    def test_extract_orders_without_filters(
        self,
        mock_extract_query,
        mysql_config,
        sample_orders_df
    ):
        """Тест витягування замовлень без фільтрів."""
        mock_extract_query.return_value = sample_orders_df
        
        extractor = OrdersExtractor(mysql_config)
        result = extractor.extract_orders()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        mock_extract_query.assert_called_once()
    
    @patch('etl.extract.Extractor.extract_query')
    def test_extract_orders_with_date_filters(
        self,
        mock_extract_query,
        mysql_config,
        sample_orders_df
    ):
        """Тест витягування замовлень з фільтрами по даті."""
        mock_extract_query.return_value = sample_orders_df
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        extractor = OrdersExtractor(mysql_config)
        result = extractor.extract_orders(start_date=start_date, end_date=end_date)
        
        assert isinstance(result, pd.DataFrame)
        mock_extract_query.assert_called_once()
    
    @patch('etl.extract.Extractor.extract_query')
    def test_extract_customers(self, mock_extract_query, mysql_config):
        """Тест витягування клієнтів."""
        expected_df = pd.DataFrame({
            'customer_id': ['cust1', 'cust2'],
            'first_name': ['John', 'Jane'],
            'last_name': ['Doe', 'Smith'],
            'email': ['john@example.com', 'jane@example.com']
        })
        mock_extract_query.return_value = expected_df
        
        extractor = OrdersExtractor(mysql_config)
        result = extractor.extract_customers()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'customer_id' in result.columns
    
    @patch('etl.extract.Extractor.extract_query')
    def test_extract_employees(self, mock_extract_query, mysql_config):
        """Тест витягування співробітників."""
        expected_df = pd.DataFrame({
            'employee_id': ['emp1', 'emp2'],
            'first_name': ['Manager', 'Sales'],
            'is_manager': [True, False],
            'region_id': ['reg1', 'reg2']
        })
        mock_extract_query.return_value = expected_df
        
        extractor = OrdersExtractor(mysql_config)
        result = extractor.extract_employees()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'is_manager' in result.columns
    
    @patch('etl.extract.Extractor.extract_query')
    def test_extract_regions(self, mock_extract_query, mysql_config):
        """Тест витягування регіонів."""
        expected_df = pd.DataFrame({
            'region_id': ['reg1', 'reg2'],
            'region_name': ['Київська', 'Львівська'],
            'region_code': ['KYI', 'LVI']
        })
        mock_extract_query.return_value = expected_df
        
        extractor = OrdersExtractor(mysql_config)
        result = extractor.extract_regions()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'region_name' in result.columns


class TestCatalogExtractor:
    """Тести для CatalogExtractor."""
    
    @patch('etl.extract.Extractor.extract_query')
    def test_extract_products(self, mock_extract_query, mysql_config):
        """Тест витягування товарів."""
        expected_df = pd.DataFrame({
            'product_id': ['prod1', 'prod2'],
            'product_name': ['Product 1', 'Product 2'],
            'price': [100.0, 200.0],
            'category_id': ['cat1', 'cat2']
        })
        mock_extract_query.return_value = expected_df
        
        extractor = CatalogExtractor(mysql_config)
        result = extractor.extract_products()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'product_name' in result.columns
        assert 'price' in result.columns
    
    @patch('etl.extract.Extractor.extract_query')
    def test_extract_categories(self, mock_extract_query, mysql_config):
        """Тест витягування категорій."""
        expected_df = pd.DataFrame({
            'category_id': ['cat1', 'cat2', 'cat3'],
            'category_name': ['Electronics', 'Laptops', 'Gaming'],
            'parent_category_id': [None, 'cat1', 'cat2']
        })
        mock_extract_query.return_value = expected_df
        
        extractor = CatalogExtractor(mysql_config)
        result = extractor.extract_categories()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'parent_category_id' in result.columns


class TestPaymentsExtractor:
    """Тести для PaymentsExtractor."""
    
    @patch('etl.extract.Extractor.extract_query')
    def test_extract_payments(self, mock_extract_query, mysql_config):
        """Тест витягування платежів."""
        expected_df = pd.DataFrame({
            'payment_id': ['pay1', 'pay2'],
            'order_id': ['order1', 'order2'],
            'amount': [100.0, 200.0],
            'payment_method': ['card', 'paypal'],
            'payment_date': pd.to_datetime(['2024-01-01', '2024-01-02']),
            'payment_status': ['completed', 'completed']
        })
        mock_extract_query.return_value = expected_df
        
        extractor = PaymentsExtractor(mysql_config)
        result = extractor.extract_payments()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'payment_method' in result.columns
    
    @patch('etl.extract.Extractor.extract_query')
    def test_extract_payments_with_date_filters(
        self,
        mock_extract_query,
        mysql_config
    ):
        """Тест витягування платежів з фільтрами."""
        expected_df = pd.DataFrame({
            'payment_id': ['pay1'],
            'order_id': ['order1'],
            'amount': [100.0],
            'payment_date': pd.to_datetime(['2024-01-01'])
        })
        mock_extract_query.return_value = expected_df
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        extractor = PaymentsExtractor(mysql_config)
        result = extractor.extract_payments(start_date=start_date, end_date=end_date)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
