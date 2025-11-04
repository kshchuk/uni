"""
Тести для Load модуля.

Перевіряє коректність завантаження даних у DWH.
"""

import pytest
import pandas as pd
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from etl.config import PostgreSQLConfig
from etl.load import Loader


@pytest.fixture
def postgres_config():
    """Фікстура з конфігурацією PostgreSQL."""
    return PostgreSQLConfig(
        host='localhost',
        port=5432,
        database='test_dwh',
        user='test_user',
        password='test_pass'
    )


@pytest.fixture
def sample_dimension_df():
    """Фікстура з даними для dimension."""
    return pd.DataFrame({
        'region_id': ['reg1', 'reg2', 'reg3'],
        'region_name': ['Region 1', 'Region 2', 'Region 3'],
        'country': ['USA', 'Canada', 'UK']
    })


@pytest.fixture
def sample_fact_df():
    """Фікстура з даними для fact."""
    return pd.DataFrame({
        'order_id': ['order1', 'order2', 'order3'],
        'order_item_id': ['item1', 'item2', 'item3'],
        'date_key': [20240101, 20240102, 20240103],
        'product_id': ['prod1', 'prod2', 'prod3'],
        'customer_id': ['cust1', 'cust1', 'cust2'],
        'employee_id': ['emp1', 'emp2', 'emp1'],
        'region_id': ['reg1', 'reg1', 'reg2'],
        'quantity': [2, 3, 1],
        'revenue': [200.0, 450.0, 200.0],
        'discount_amount': [10.0, 0.0, 20.0],
        'cost': [120.0, 270.0, 120.0],
        'margin': [80.0, 180.0, 80.0]
    })


class TestLoader:
    """Тести для Loader."""
    
    @patch('etl.load.create_engine')
    def test_init(self, mock_create_engine, postgres_config):
        """Тест ініціалізації Loader."""
        loader = Loader(postgres_config)
        
        assert loader.config == postgres_config
        assert loader._engine is None  # Engine створюється лише при доступі
    
    @patch('etl.load.create_engine')
    def test_engine_property(self, mock_create_engine, postgres_config):
        """Тест створення engine через property."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        loader = Loader(postgres_config)
        engine = loader.engine
        
        assert engine == mock_engine
        mock_create_engine.assert_called_once_with(
            postgres_config.connection_string,
            pool_pre_ping=True,
            pool_recycle=3600
        )
    
    @patch('etl.load.create_engine')
    def test_engine_cached(self, mock_create_engine, postgres_config):
        """Тест що engine кешується."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        loader = Loader(postgres_config)
        engine1 = loader.engine
        engine2 = loader.engine
        
        assert engine1 is engine2
        mock_create_engine.assert_called_once()
    
    @patch('etl.load.create_engine')
    def test_load_dimension(self, mock_create_engine, postgres_config, sample_dimension_df):
        """Тест завантаження dimension."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        loader = Loader(postgres_config)
        
        with patch.object(pd.DataFrame, 'to_sql') as mock_to_sql:
            loader.load_dimension(
                df=sample_dimension_df,
                table_name='dim_region',
                if_exists='replace'
            )
            
            mock_to_sql.assert_called_once_with(
                'dim_region',
                mock_engine,
                if_exists='replace',
                index=False,
                chunksize=1000,
                method='multi'
            )
    
    @patch('etl.load.create_engine')
    def test_load_fact_sales(self, mock_create_engine, postgres_config, sample_fact_df):
        """Тест завантаження fact_sales."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        loader = Loader(postgres_config)
        
        with patch.object(pd.DataFrame, 'to_sql') as mock_to_sql:
            loader.load_fact_sales(sample_fact_df)
            
            mock_to_sql.assert_called_once()
            args, kwargs = mock_to_sql.call_args
            assert args[0] == 'fact_sales'
    
    @patch('etl.load.create_engine')
    def test_load_fact_sales_validates_columns(self, mock_create_engine, postgres_config):
        """Тест валідації обов'язкових колонок у fact_sales."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        # DataFrame без обов'язкових колонок
        invalid_df = pd.DataFrame({
            'date_key': [20240101],
            'product_id': ['prod1']
            # відсутні інші обов'язкові колонки
        })
        
        loader = Loader(postgres_config)
        
        with pytest.raises(ValueError, match="Відсутні необхідні колонки"):
            loader.load_fact_sales(invalid_df)
    
    @patch('etl.load.create_engine')
    def test_load_dim_date(self, mock_create_engine, postgres_config):
        """Тест завантаження календаря."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        loader = Loader(postgres_config)
        
        with patch.object(pd.DataFrame, 'to_sql') as mock_to_sql:
            loader.load_dim_date(
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 3)
            )
            
            mock_to_sql.assert_called_once()
    
    @patch('etl.load.create_engine')
    def test_get_existing_keys(self, mock_create_engine, postgres_config):
        """Тест отримання існуючих ключів."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        # Mock для read_sql
        expected_keys = {'key1', 'key2', 'key3'}
        mock_df = pd.DataFrame({'product_id': list(expected_keys)})
        
        loader = Loader(postgres_config)
        
        with patch('pandas.read_sql', return_value=mock_df) as mock_read_sql:
            result = loader.get_existing_keys('dim_product', 'product_id')
            
            assert result == expected_keys
            mock_read_sql.assert_called_once()
    
    @patch('etl.load.create_engine')
    def test_upsert_dimension(self, mock_create_engine, postgres_config, sample_dimension_df):
        """Тест upsert для dimension."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        loader = Loader(postgres_config)
        
        # Mock для get_existing_keys
        existing_keys = {'reg1'}
        
        with patch.object(loader, 'get_existing_keys', return_value=existing_keys):
            with patch.object(pd.DataFrame, 'to_sql') as mock_to_sql:
                loader.upsert_dimension(
                    df=sample_dimension_df,
                    table_name='dim_region',
                    key_column='region_id'
                )
                
                # Повинно викликатися двічі: для нових та для оновлення
                assert mock_to_sql.call_count == 2
    
    @patch('etl.load.create_engine')
    def test_upsert_dimension_no_new_records(self, mock_create_engine, postgres_config):
        """Тест upsert коли немає нових записів."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        df = pd.DataFrame({
            'region_id': ['reg1'],
            'region_name': ['Region 1']
        })
        
        loader = Loader(postgres_config)
        
        # Всі ключі вже існують
        existing_keys = {'reg1'}
        
        with patch.object(loader, 'get_existing_keys', return_value=existing_keys):
            with patch.object(pd.DataFrame, 'to_sql') as mock_to_sql:
                loader.upsert_dimension(
                    df=df,
                    table_name='dim_region',
                    key_column='region_id'
                )
                
                # Тільки update, без insert
                assert mock_to_sql.call_count == 1
    
    @patch('etl.load.create_engine')
    def test_close(self, mock_create_engine, postgres_config):
        """Тест закриття з'єднання."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        loader = Loader(postgres_config)
        _ = loader.engine  # Створюємо engine
        
        loader.close()
        
        mock_engine.dispose.assert_called_once()
    
    @patch('etl.load.create_engine')
    def test_close_no_engine(self, mock_create_engine, postgres_config):
        """Тест закриття без створеного engine."""
        loader = Loader(postgres_config)
        
        # Не повинно викликати помилки
        loader.close()
        
        mock_create_engine.assert_not_called()
