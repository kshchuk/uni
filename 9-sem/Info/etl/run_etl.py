#!/usr/bin/env python3
"""
Скрипт для запуску ETL pipeline.

Використання:
    # Повне завантаження
    python run_etl.py --mode full
    
    # Інкрементальне завантаження
    python run_etl.py --mode incremental --start-date 2024-01-01 --end-date 2024-01-31
    
    # З вказаним .env файлом
    python run_etl.py --mode full --env-file /path/to/.env
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from etl.config import ETLConfig
from etl.pipeline import ETLPipeline


# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('etl.log')
    ]
)

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Парсить аргументи командного рядка.
    
    Returns:
        Аргументи командного рядка
    """
    parser = argparse.ArgumentParser(
        description='Запуск ETL pipeline для TechMarket DWH'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['full', 'incremental'],
        required=True,
        help='Режим завантаження: full або incremental'
    )
    
    parser.add_argument(
        '--start-date',
        type=str,
        help='Початкова дата для інкрементального завантаження (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        help='Кінцева дата для інкрементального завантаження (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--env-file',
        type=str,
        default='.env',
        help='Шлях до .env файлу (за замовчуванням: .env)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Рівень логування'
    )
    
    return parser.parse_args()


def validate_dates(
    mode: str,
    start_date: Optional[str],
    end_date: Optional[str]
) -> tuple[Optional[datetime], Optional[datetime]]:
    """Валідує та конвертує дати.
    
    Args:
        mode: Режим завантаження
        start_date: Початкова дата (рядок)
        end_date: Кінцева дата (рядок)
    
    Returns:
        Кортеж з datetime об'єктами
        
    Raises:
        ValueError: Якщо дати некоректні
    """
    if mode == 'incremental':
        if not start_date or not end_date:
            raise ValueError(
                "Для incremental режиму потрібно вказати --start-date та --end-date"
            )
        
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Неправильний формат дати. Використовуйте YYYY-MM-DD: {e}")
        
        if start_dt > end_dt:
            raise ValueError("Початкова дата не може бути пізніше кінцевої")
        
        return start_dt, end_dt
    
    return None, None


def main() -> int:
    """Головна функція.
    
    Returns:
        Код виходу (0 - успіх, 1 - помилка)
    """
    args = parse_args()
    
    # Налаштування рівня логування
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        logger.info("=" * 60)
        logger.info("Початок ETL процесу")
        logger.info(f"Режим: {args.mode}")
        logger.info(f"Конфігураційний файл: {args.env_file}")
        logger.info("=" * 60)
        
        # Перевірка наявності .env файлу
        env_path = Path(args.env_file)
        if not env_path.exists():
            logger.error(f"Конфігураційний файл не знайдено: {args.env_file}")
            logger.info("Створіть .env файл на основі .env.example")
            return 1
        
        # Валідація дат
        start_dt, end_dt = validate_dates(args.mode, args.start_date, args.end_date)
        
        if start_dt and end_dt:
            logger.info(f"Період: {start_dt.date()} - {end_dt.date()}")
        
        # Завантаження конфігурації
        logger.info("Завантаження конфігурації...")
        config = ETLConfig.from_env()
        
        # Створення pipeline
        logger.info("Ініціалізація ETL pipeline...")
        pipeline = ETLPipeline(config)
        
        # Запуск ETL
        if args.mode == 'full':
            logger.info("Запуск повного завантаження...")
            results = pipeline.run_full_load()
        else:
            logger.info("Запуск інкрементального завантаження...")
            results = pipeline.run_incremental_load(start_dt, end_dt)
        
        # Виведення результатів
        logger.info("=" * 60)
        logger.info("ETL процес завершено успішно!")
        logger.info("Результати:")
        for table, count in results.items():
            logger.info(f"  {table}: {count:,} записів")
        logger.info("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("ETL процес перервано користувачем")
        return 1
    except Exception as e:
        logger.error(f"Помилка виконання ETL: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
