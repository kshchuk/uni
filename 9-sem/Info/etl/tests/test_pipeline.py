"""
Тести для Pipeline модуля.

Перевіряє коректність оркестрації ETL процесу.
"""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, call

from etl.config import ETLConfig, MySQLConfig, PostgreSQLConfig
from etl.pipeline import ETLPipeline


@pytest.fixture
def etl_config():
    """Фікстура з конфігурацією ETL."""
    return ETLConfig(
        auth_db=MySQLConfig(
            host='localhost',
            port=3306,
            database='test_auth',
            user='test_user',
            password='test_pass'
        ),
        orders_db=MySQLConfig(
            host='localhost',
            port=3306,
            database='test_orders',
            user='test_user',
            password='test_pass'
        ),
        catalog_db=MySQLConfig(
            host='localhost',
            port=3306,
            database='test_catalog',
            user='test_user',
            password='test_pass'
        ),
        payments_db=MySQLConfig(
            host='localhost',
            port=3306,
            database='test_payments',
            user='test_user',
            password='test_pass'
        ),
        dwh_db=PostgreSQLConfig(
            host='localhost',
            port=5432,
            database='test_dwh',
            user='test_user',
            password='test_pass'
        ),
        incremental=False
    )


@pytest.fixture
def sample_regions_df():
    """Фікстура з регіонами."""
    return pd.DataFrame({
        'region_id': ['reg1', 'reg2'],
        'region_name': ['Region 1', 'Region 2'],
        'country': ['USA', 'Canada']
    })


@pytest.fixture
def sample_categories_df():
    """Фікстура з категоріями."""
    return pd.DataFrame({
        'category_id': ['cat1', 'cat2'],
        'category_name': ['Category 1', 'Category 2']
    })


@pytest.fixture
def sample_products_df():
    """Фікстура з товарами."""
    return pd.DataFrame({
        'product_id': ['prod1', 'prod2'],
        'product_name': ['Product 1', 'Product 2'],
        'price': [100.0, 200.0],
        'category_id': ['cat1', 'cat2'],
        'category_name': ['Category 1', 'Category 2']
    })


@pytest.fixture
def sample_customers_df():
    """Фікстура з клієнтами."""
    return pd.DataFrame({
        'customer_id': ['cust1', 'cust2'],
        'first_name': ['John', 'Jane'],
        'last_name': ['Doe', 'Smith'],
        'email': ['john@example.com', 'jane@example.com']
    })


@pytest.fixture
def sample_employees_df():
    """Фікстура зі співробітниками."""
    return pd.DataFrame({
        'employee_id': ['emp1', 'emp2'],
        'first_name': ['Alice', 'Bob'],
        'last_name': ['Johnson', 'Williams'],
        'email': ['alice@example.com', 'bob@example.com']
    })


@pytest.fixture
def sample_orders_df():
    """Фікстура із замовленнями."""
    return pd.DataFrame({
        'order_id': ['order1', 'order2'],
        'order_item_id': ['item1', 'item2'],
        'order_date': pd.to_datetime(['2024-01-01', '2024-01-02']),
        'customer_id': ['cust1', 'cust2'],
        'employee_id': ['emp1', 'emp2'],
        'region_id': ['reg1', 'reg2'],
        'product_id': ['prod1', 'prod2'],
        'quantity': [2, 3],
        'unit_price': [100.0, 150.0],
        'discount': [10.0, 0.0],
        'total_amount': [190.0, 450.0]
    })


class TestETLPipeline:
    """Тести для ETLPipeline."""
    
    @patch('etl.pipeline.Loader')
    @patch('etl.pipeline.DataTransformer')
    @patch('etl.pipeline.PaymentsExtractor')
    @patch('etl.pipeline.CatalogExtractor')
    @patch('etl.pipeline.OrdersExtractor')
    def test_init(
        self,
        mock_orders_extractor,
        mock_catalog_extractor,
        mock_payments_extractor,
        mock_transformer,
        mock_loader,
        etl_config
    ):
        """Тест ініціалізації pipeline."""
        pipeline = ETLPipeline(etl_config)
        
        assert pipeline.config == etl_config
        mock_orders_extractor.assert_called_once_with(etl_config.orders_db)
        mock_catalog_extractor.assert_called_once_with(etl_config.catalog_db)
        mock_payments_extractor.assert_called_once_with(etl_config.payments_db)
        mock_transformer.assert_called_once()
        mock_loader.assert_called_once_with(etl_config.dwh_db)
    
    @patch('etl.pipeline.Loader')
    @patch('etl.pipeline.DataTransformer')
    @patch('etl.pipeline.PaymentsExtractor')
    @patch('etl.pipeline.CatalogExtractor')
    @patch('etl.pipeline.OrdersExtractor')
    def test_load_dim_date(
        self,
        mock_orders_extractor,
        mock_catalog_extractor,
        mock_payments_extractor,
        mock_transformer,
        mock_loader,
        etl_config
    ):
        """Тест завантаження dim_date."""
        pipeline = ETLPipeline(etl_config)
        
        pipeline._load_dim_date()
        
        pipeline.loader.load_dim_date.assert_called_once()
    
    @patch('etl.pipeline.Loader')
    @patch('etl.pipeline.DataTransformer')
    @patch('etl.pipeline.PaymentsExtractor')
    @patch('etl.pipeline.CatalogExtractor')
    @patch('etl.pipeline.OrdersExtractor')
    def test_load_dim_region(
        self,
        mock_orders_extractor,
        mock_catalog_extractor,
        mock_payments_extractor,
        mock_transformer,
        mock_loader,
        etl_config,
        sample_regions_df
    ):
        """Тест завантаження dim_region."""
        pipeline = ETLPipeline(etl_config)
        
        # Mock extractor instance
        mock_extractor_instance = Mock()
        mock_extractor_instance.extract_regions.return_value = sample_regions_df
        pipeline.orders_extractor = mock_extractor_instance
        
        # Mock loader instance
        mock_loader_instance = Mock()
        mock_loader_instance.load_dimension.return_value = len(sample_regions_df)
        pipeline.loader = mock_loader_instance
        
        result = pipeline._load_dim_region()
        
        mock_extractor_instance.extract_regions.assert_called_once()
        mock_loader_instance.load_dimension.assert_called_once()
        assert result == len(sample_regions_df)
    
    @patch('etl.pipeline.Loader')
    @patch('etl.pipeline.DataTransformer')
    @patch('etl.pipeline.PaymentsExtractor')
    @patch('etl.pipeline.CatalogExtractor')
    @patch('etl.pipeline.OrdersExtractor')
    def test_load_dim_category(
        self,
        mock_orders_extractor,
        mock_catalog_extractor,
        mock_payments_extractor,
        mock_transformer,
        mock_loader,
        etl_config,
        sample_categories_df
    ):
        """Тест завантаження dim_category."""
        pipeline = ETLPipeline(etl_config)
        
        # Mock instances
        mock_catalog_instance = Mock()
        mock_catalog_instance.extract_categories.return_value = sample_categories_df
        pipeline.catalog_extractor = mock_catalog_instance
        
        mock_loader_instance = Mock()
        mock_loader_instance.load_dimension.return_value = len(sample_categories_df)
        pipeline.loader = mock_loader_instance
        
        result = pipeline._load_dim_category()
        
        mock_catalog_instance.extract_categories.assert_called_once()
        mock_loader_instance.load_dimension.assert_called_once()
        assert result == len(sample_categories_df)
    
    @patch('etl.pipeline.Loader')
    @patch('etl.pipeline.DataTransformer')
    @patch('etl.pipeline.PaymentsExtractor')
    @patch('etl.pipeline.CatalogExtractor')
    @patch('etl.pipeline.OrdersExtractor')
    def test_load_dim_product(
        self,
        mock_orders_extractor,
        mock_catalog_extractor,
        mock_payments_extractor,
        mock_transformer,
        mock_loader,
        etl_config,
        sample_products_df
    ):
        """Тест завантаження dim_product."""
        pipeline = ETLPipeline(etl_config)
        pipeline.catalog_extractor.extract_products.return_value = sample_products_df
        pipeline.transformer.transform_products.return_value = sample_products_df
        
        pipeline._load_dim_product()
        
        pipeline.catalog_extractor.extract_products.assert_called_once()
        pipeline.transformer.transform_products.assert_called_once_with(sample_products_df)
        pipeline.loader.load_dimension.assert_called_once()
    
    @patch('etl.pipeline.Loader')
    @patch('etl.pipeline.DataTransformer')
    @patch('etl.pipeline.PaymentsExtractor')
    @patch('etl.pipeline.CatalogExtractor')
    @patch('etl.pipeline.OrdersExtractor')
    def test_load_dim_customer(
        self,
        mock_orders_extractor,
        mock_catalog_extractor,
        mock_payments_extractor,
        mock_transformer,
        mock_loader,
        etl_config,
        sample_customers_df
    ):
        """Тест завантаження dim_customer."""
        pipeline = ETLPipeline(etl_config)
        pipeline.orders_extractor.extract_customers.return_value = sample_customers_df
        pipeline.transformer.transform_customers.return_value = sample_customers_df
        
        pipeline._load_dim_customer()
        
        pipeline.orders_extractor.extract_customers.assert_called_once()
        pipeline.transformer.transform_customers.assert_called_once_with(sample_customers_df)
        pipeline.loader.load_dimension.assert_called_once()
    
    @patch('etl.pipeline.Loader')
    @patch('etl.pipeline.DataTransformer')
    @patch('etl.pipeline.PaymentsExtractor')
    @patch('etl.pipeline.CatalogExtractor')
    @patch('etl.pipeline.OrdersExtractor')
    def test_load_dim_employee(
        self,
        mock_orders_extractor,
        mock_catalog_extractor,
        mock_payments_extractor,
        mock_transformer,
        mock_loader,
        etl_config,
        sample_employees_df
    ):
        """Тест завантаження dim_employee."""
        pipeline = ETLPipeline(etl_config)
        pipeline.orders_extractor.extract_employees.return_value = sample_employees_df
        
        pipeline._load_dim_employee()
        
        pipeline.orders_extractor.extract_employees.assert_called_once()
        pipeline.loader.load_dimension.assert_called_once()
    
    @patch('etl.pipeline.Loader')
    @patch('etl.pipeline.DataTransformer')
    @patch('etl.pipeline.PaymentsExtractor')
    @patch('etl.pipeline.CatalogExtractor')
    @patch('etl.pipeline.OrdersExtractor')
    def test_load_fact_sales(
        self,
        mock_orders_extractor,
        mock_catalog_extractor,
        mock_payments_extractor,
        mock_transformer,
        mock_loader,
        etl_config,
        sample_orders_df
    ):
        """Тест завантаження fact_sales."""
        pipeline = ETLPipeline(etl_config)
        pipeline.orders_extractor.extract_orders.return_value = sample_orders_df
        
        transformed_df = sample_orders_df.copy()
        transformed_df['revenue'] = 200.0
        pipeline.transformer.transform_orders.return_value = transformed_df
        
        pipeline._load_fact_sales()
        
        pipeline.orders_extractor.extract_orders.assert_called_once()
        pipeline.transformer.transform_orders.assert_called_once_with(sample_orders_df)
        pipeline.loader.load_fact_sales.assert_called_once()
    
    @patch('etl.pipeline.Loader')
    @patch('etl.pipeline.DataTransformer')
    @patch('etl.pipeline.PaymentsExtractor')
    @patch('etl.pipeline.CatalogExtractor')
    @patch('etl.pipeline.OrdersExtractor')
    def test_run_full_load(
        self,
        mock_orders_extractor,
        mock_catalog_extractor,
        mock_payments_extractor,
        mock_transformer,
        mock_loader,
        etl_config
    ):
        """Тест повного завантаження."""
        pipeline = ETLPipeline(etl_config)
        
        # Mock всі методи завантаження
        with patch.object(pipeline, '_load_dim_date'):
            with patch.object(pipeline, '_load_dim_region'):
                with patch.object(pipeline, '_load_dim_category'):
                    with patch.object(pipeline, '_load_dim_product'):
                        with patch.object(pipeline, '_load_dim_customer'):
                            with patch.object(pipeline, '_load_dim_employee'):
                                with patch.object(pipeline, '_load_fact_sales'):
                                    pipeline.run_full_load()
                                    
                                    # Перевіряємо що всі методи викликані
                                    pipeline._load_dim_date.assert_called_once()
                                    pipeline._load_dim_region.assert_called_once()
                                    pipeline._load_dim_category.assert_called_once()
                                    pipeline._load_dim_product.assert_called_once()
                                    pipeline._load_dim_customer.assert_called_once()
                                    pipeline._load_dim_employee.assert_called_once()
                                    pipeline._load_fact_sales.assert_called_once()
    
    @patch('etl.pipeline.Loader')
    @patch('etl.pipeline.DataTransformer')
    @patch('etl.pipeline.PaymentsExtractor')
    @patch('etl.pipeline.CatalogExtractor')
    @patch('etl.pipeline.OrdersExtractor')
    def test_cleanup(
        self,
        mock_orders_extractor,
        mock_catalog_extractor,
        mock_payments_extractor,
        mock_transformer,
        mock_loader,
        etl_config
    ):
        """Тест очищення ресурсів."""
        pipeline = ETLPipeline(etl_config)
        
        pipeline._cleanup()
        
        # Перевіряємо що викликано close для всіх extractors та loader
        pipeline.orders_extractor.close.assert_called_once()
        pipeline.catalog_extractor.close.assert_called_once()
        pipeline.payments_extractor.close.assert_called_once()
        pipeline.loader.close.assert_called_once()
    
    @patch('etl.pipeline.Loader')
    @patch('etl.pipeline.DataTransformer')
    @patch('etl.pipeline.PaymentsExtractor')
    @patch('etl.pipeline.CatalogExtractor')
    @patch('etl.pipeline.OrdersExtractor')
    def test_run_full_load_with_error(
        self,
        mock_orders_extractor,
        mock_catalog_extractor,
        mock_payments_extractor,
        mock_transformer,
        mock_loader,
        etl_config
    ):
        """Тест обробки помилки при повному завантаженні."""
        pipeline = ETLPipeline(etl_config)
        
        # Викликаємо помилку в одному з методів
        with patch.object(pipeline, '_load_dim_date', side_effect=Exception("Test error")):
            with patch.object(pipeline, '_cleanup'):
                with pytest.raises(Exception, match="Test error"):
                    pipeline.run_full_load()
                
                # Перевіряємо що cleanup викликано
                pipeline._cleanup.assert_called_once()
