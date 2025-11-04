"""
Головний ETL pipeline для TechMarket DWH.

Координує процес витягування, трансформації та завантаження даних.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from .config import ETLConfig
from .extract import OrdersExtractor, CatalogExtractor, PaymentsExtractor
from .transform import DataTransformer
from .load import Loader

logger = logging.getLogger(__name__)


class ETLPipeline:
    """Головний клас ETL pipeline.
    
    Attributes:
        config: Конфігурація ETL процесу
        orders_extractor: Екстрактор для Orders DB
        catalog_extractor: Екстрактор для Catalog DB
        payments_extractor: Екстрактор для Payments DB
        transformer: Трансформер даних
        loader: Лоадер для DWH
    """
    
    def __init__(self, config: ETLConfig):
        """Ініціалізує ETL pipeline.
        
        Args:
            config: Конфігурація ETL процесу
        """
        self.config = config
        
        # Ініціалізація екстракторів
        self.orders_extractor = OrdersExtractor(config.orders_db)
        self.catalog_extractor = CatalogExtractor(config.catalog_db)
        self.payments_extractor = PaymentsExtractor(config.payments_db)
        
        # Ініціалізація трансформера та лоадера
        self.transformer = DataTransformer()
        self.loader = Loader(config.dwh_db)
        
        # Налаштування логування
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def run_full_load(self) -> dict[str, int]:
        """Виконує повне завантаження всіх даних.
        
        Returns:
            Словник з кількістю завантажених записів для кожної таблиці
        """
        logger.info("=" * 60)
        logger.info("Початок повного ETL процесу")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        results = {}
        
        try:
            # 1. Завантаження dim_date
            logger.info("\n[1/7] Завантаження dim_date")
            results['dim_date'] = self._load_dim_date()
            
            # 2. Завантаження dim_region
            logger.info("\n[2/7] Завантаження dim_region")
            results['dim_region'] = self._load_dim_region()
            
            # 3. Завантаження dim_category та dim_product
            logger.info("\n[3/7] Завантаження dim_category та dim_product")
            results['dim_category'] = self._load_dim_category()
            results['dim_product'] = self._load_dim_product()
            
            # 4. Завантаження dim_customer
            logger.info("\n[4/7] Завантаження dim_customer")
            results['dim_customer'] = self._load_dim_customer()
            
            # 5. Завантаження dim_employee
            logger.info("\n[5/7] Завантаження dim_employee")
            results['dim_employee'] = self._load_dim_employee()
            
            # 6. Завантаження fact_sales
            logger.info("\n[6/7] Завантаження fact_sales")
            results['fact_sales'] = self._load_fact_sales()
            
            # 7. Статистика
            logger.info("\n[7/7] Завершення ETL")
            elapsed_time = datetime.now() - start_time
            
            logger.info("=" * 60)
            logger.info("ETL процес завершено успішно")
            logger.info(f"Час виконання: {elapsed_time}")
            logger.info("Завантажено записів:")
            for table, count in results.items():
                logger.info(f"  {table}: {count}")
            logger.info("=" * 60)
            
            return results
            
        except Exception as e:
            logger.error(f"Помилка виконання ETL: {e}", exc_info=True)
            raise
        finally:
            self._cleanup()
    
    def run_incremental_load(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict[str, int]:
        """Виконує інкрементальне завантаження за період.
        
        Args:
            start_date: Початкова дата (за замовчуванням - вчора)
            end_date: Кінцева дата (за замовчуванням - сьогодні)
            
        Returns:
            Словник з кількістю завантажених записів
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=1)
        if end_date is None:
            end_date = datetime.now()
        
        logger.info("=" * 60)
        logger.info(f"Інкрементальне завантаження: {start_date} - {end_date}")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        results = {}
        
        try:
            # Завантажуємо тільки нові дані
            results['fact_sales'] = self._load_fact_sales_incremental(start_date, end_date)
            
            elapsed_time = datetime.now() - start_time
            logger.info(f"Інкрементальне завантаження завершено за {elapsed_time}")
            
            return results
            
        except Exception as e:
            logger.error(f"Помилка інкрементального завантаження: {e}", exc_info=True)
            raise
        finally:
            self._cleanup()
    
    def _load_dim_date(self) -> int:
        """Завантажує dim_date."""
        # Генеруємо календар на 2 роки (730 днів)
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now() + timedelta(days=365)
        return self.loader.load_dim_date(start_date, end_date)
    
    def _load_dim_region(self) -> int:
        """Завантажує dim_region."""
        df_regions = self.orders_extractor.extract_regions()
        df_regions_transformed = self.transformer.cleaner.remove_duplicates(
            df_regions,
            subset=['region_id']
        )
        return self.loader.load_dimension(df_regions_transformed, 'dim_region', 'replace')
    
    def _load_dim_category(self) -> int:
        """Завантажує dim_category."""
        df_categories = self.catalog_extractor.extract_categories()
        df_categories_transformed = self.transformer.cleaner.remove_duplicates(
            df_categories,
            subset=['category_id']
        )
        return self.loader.load_dimension(df_categories_transformed, 'dim_category', 'replace')
    
    def _load_dim_product(self) -> int:
        """Завантажує dim_product."""
        df_products = self.catalog_extractor.extract_products()
        df_products_transformed = self.transformer.transform_products(df_products)
        return self.loader.load_dimension(df_products_transformed, 'dim_product', 'replace')
    
    def _load_dim_customer(self) -> int:
        """Завантажує dim_customer."""
        df_customers = self.orders_extractor.extract_customers()
        df_customers_transformed = self.transformer.transform_customers(df_customers)
        return self.loader.load_dimension(df_customers_transformed, 'dim_customer', 'replace')
    
    def _load_dim_employee(self) -> int:
        """Завантажує dim_employee."""
        df_employees = self.orders_extractor.extract_employees()
        df_employees_transformed = self.transformer.cleaner.remove_duplicates(
            df_employees,
            subset=['employee_id']
        )
        return self.loader.load_dimension(df_employees_transformed, 'dim_employee', 'replace')
    
    def _load_fact_sales(self) -> int:
        """Завантажує fact_sales (повне завантаження)."""
        # Витягуємо замовлення
        df_orders = self.orders_extractor.extract_orders()
        
        # Трансформуємо
        df_orders_transformed = self.transformer.transform_orders(df_orders)
        
        # Очищаємо fact_sales перед повним завантаженням
        self.loader.truncate_table('fact_sales')
        
        # Завантажуємо
        return self.loader.load_fact_sales(df_orders_transformed, if_exists='append')
    
    def _load_fact_sales_incremental(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Завантажує fact_sales інкрементально."""
        # Витягуємо тільки нові замовлення
        df_orders = self.orders_extractor.extract_orders(start_date, end_date)
        
        if len(df_orders) == 0:
            logger.info("Нових замовлень не знайдено")
            return 0
        
        # Трансформуємо
        df_orders_transformed = self.transformer.transform_orders(df_orders)
        
        # Завантажуємо (додаємо до існуючих)
        return self.loader.load_fact_sales(df_orders_transformed, if_exists='append')
    
    def _cleanup(self) -> None:
        """Очищає ресурси після завершення ETL."""
        logger.info("Закриття з'єднань...")
        self.orders_extractor.close()
        self.catalog_extractor.close()
        self.payments_extractor.close()
        self.loader.close()
        logger.info("Ресурси звільнено")


def main() -> None:
    """Головна функція для запуску ETL."""
    # Завантажуємо конфігурацію
    config = ETLConfig.from_env()
    
    # Створюємо pipeline
    pipeline = ETLPipeline(config)
    
    # Запускаємо ETL
    if config.incremental:
        pipeline.run_incremental_load()
    else:
        pipeline.run_full_load()


if __name__ == "__main__":
    main()
