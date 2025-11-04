"""
Приклади використання TechMarket ETL Pipeline.

Цей файл демонструє різні сценарії запуску ETL.
"""

from datetime import datetime, timedelta
from etl.config import ETLConfig
from etl.pipeline import ETLPipeline


def example_full_load():
    """Приклад повного завантаження."""
    print("=" * 60)
    print("Приклад 1: Повне завантаження")
    print("=" * 60)
    
    # Завантаження конфігурації з .env файлу
    config = ETLConfig.from_env()
    
    # Створення pipeline
    pipeline = ETLPipeline(config)
    
    # Виконання повного завантаження
    try:
        results = pipeline.run_full_load()
        
        print("\n✅ Успішно завантажено:")
        for table, count in results.items():
            print(f"  {table}: {count:,} записів")
            
    except Exception as e:
        print(f"\n❌ Помилка: {e}")


def example_incremental_load():
    """Приклад інкрементального завантаження."""
    print("\n" + "=" * 60)
    print("Приклад 2: Інкрементальне завантаження")
    print("=" * 60)
    
    # Налаштування дат
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)  # Останні 7 днів
    
    print(f"Період: {start_date.date()} - {end_date.date()}")
    
    config = ETLConfig.from_env()
    pipeline = ETLPipeline(config)
    
    try:
        results = pipeline.run_incremental_load(start_date, end_date)
        
        print("\n✅ Успішно завантажено:")
        for table, count in results.items():
            print(f"  {table}: {count:,} записів")
            
    except Exception as e:
        print(f"\n❌ Помилка: {e}")


def example_extract_only():
    """Приклад екстракції даних без завантаження."""
    print("\n" + "=" * 60)
    print("Приклад 3: Тільки екстракція даних")
    print("=" * 60)
    
    from etl.extract import OrdersExtractor
    
    config = ETLConfig.from_env()
    extractor = OrdersExtractor(config.orders_db)
    
    try:
        # Отримання замовлень за останні 30 днів
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        orders_data = extractor.extract_orders(start_date, end_date)
        
        # Перевіряємо чи це DataFrame чи генератор
        import pandas as pd
        if isinstance(orders_data, pd.DataFrame):
            orders_df = orders_data
        else:
            # Якщо генератор, збираємо всі chunk'и
            orders_df = pd.concat(list(orders_data), ignore_index=True)
        
        print(f"\n✅ Отримано {len(orders_df)} замовлень")
        print(f"Колонки: {list(orders_df.columns)}")
        print(f"\nПерші 5 записів:")
        print(orders_df.head())
        
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
    finally:
        extractor.close()


def example_transform_only():
    """Приклад трансформації даних."""
    print("\n" + "=" * 60)
    print("Приклад 4: Трансформація даних")
    print("=" * 60)
    
    import pandas as pd
    from etl.transform import DataTransformer, DataCleaner
    
    # Створення тестових даних
    sample_data = pd.DataFrame({
        'order_id': ['ORD001', 'ORD002', 'ORD002', 'ORD003'],
        'order_item_id': ['ITEM001', 'ITEM002', 'ITEM002', 'ITEM003'],
        'order_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-02', '2024-01-03']),
        'created_at': pd.to_datetime(['2024-01-01 10:00', '2024-01-02 11:00', '2024-01-02 11:00', '2024-01-03 12:00']),
        'quantity': [2, 3, 3, 1],
        'unit_price': [100.0, 150.0, 150.0, 200.0],
        'discount': [10.0, 0.0, 0.0, 20.0],
        'total_amount': [190.0, 450.0, 450.0, 180.0],
        'customer_id': ['CUST001', 'CUST002', 'CUST002', 'CUST003'],
        'employee_id': ['EMP001', 'EMP002', 'EMP002', 'EMP003'],
        'region_id': ['REG001', 'REG002', 'REG002', 'REG003'],
        'product_id': ['PROD001', 'PROD002', 'PROD002', 'PROD003']
    })
    
    print(f"Оригінальні дані: {len(sample_data)} записів")
    
    # Очищення дублікатів
    cleaner = DataCleaner()
    cleaned_data = cleaner.remove_duplicates(
        sample_data,
        subset=['order_id', 'order_item_id']
    )
    
    print(f"Після видалення дублікатів: {len(cleaned_data)} записів")
    
    # Трансформація
    transformer = DataTransformer()
    transformed_data = transformer.transform_orders(cleaned_data)
    
    print(f"\n✅ Трансформовано: {len(transformed_data)} записів")
    print(f"Нові колонки: {[col for col in transformed_data.columns if col not in sample_data.columns]}")
    print(f"\nПриклад трансформованих даних:")
    print(transformed_data[['order_id', 'date_key', 'revenue', 'margin']].head())


def example_daily_etl_simulation():
    """Симуляція щоденного ETL процесу."""
    print("\n" + "=" * 60)
    print("Приклад 5: Симуляція щоденного ETL")
    print("=" * 60)
    
    from datetime import date
    
    # Симулюємо ETL за останні 7 днів
    today = date.today()
    
    print("Симуляція завантаження за останні 7 днів:")
    print()
    
    config = ETLConfig.from_env()
    
    for i in range(7, 0, -1):
        day = today - timedelta(days=i)
        start_dt = datetime.combine(day, datetime.min.time())
        end_dt = datetime.combine(day, datetime.max.time())
        
        print(f"День {8-i}/7: {day}")
        
        try:
            pipeline = ETLPipeline(config)
            results = pipeline.run_incremental_load(start_dt, end_dt)
            
            total = sum(results.values())
            print(f"  ✅ Завантажено {total:,} записів")
            
        except Exception as e:
            print(f"  ❌ Помилка: {e}")
    
    print("\n✅ Симуляція завершена")


if __name__ == '__main__':
    import sys
    
    examples = {
        '1': ('Повне завантаження', example_full_load),
        '2': ('Інкрементальне завантаження', example_incremental_load),
        '3': ('Тільки екстракція', example_extract_only),
        '4': ('Трансформація даних', example_transform_only),
        '5': ('Симуляція щоденного ETL', example_daily_etl_simulation),
    }
    
    if len(sys.argv) > 1 and sys.argv[1] in examples:
        _, func = examples[sys.argv[1]]
        func()
    else:
        print("Доступні приклади:")
        print()
        for key, (name, _) in examples.items():
            print(f"  {key}. {name}")
        print()
        print("Використання:")
        print(f"  python {sys.argv[0]} [1-5]")
        print()
        print("Або запустіть всі приклади:")
        print(f"  python {sys.argv[0]}")
        print()
        
        # Якщо аргументів немає, запускаємо всі приклади
        if len(sys.argv) == 1:
            for name, func in examples.values():
                func()
