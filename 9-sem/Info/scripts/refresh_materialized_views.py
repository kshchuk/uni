#!/usr/bin/env python3
"""
Refresh Materialized Views for TechMarket DWH

This script refreshes all materialized views after ETL runs to ensure
analytical queries have up-to-date pre-aggregated data.

Usage:
    python scripts/refresh_materialized_views.py
    
Environment variables:
    DWH_HOST: PostgreSQL host (default: localhost)
    DWH_PORT: PostgreSQL port (default: 5432)
    DWH_NAME: Database name (default: dwh_db)
    DWH_USER: Database user (default: dwh_user)
    DWH_PASS: Database password (default: dwh_pass)
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from sqlalchemy import create_engine, text
except ImportError:
    print("Error: SQLAlchemy is required. Install it with: pip install sqlalchemy psycopg2-binary")
    sys.exit(1)


def load_env_file(path: str = ".env") -> None:
    """Load environment variables from .env file if it exists."""
    env_path = Path(path)
    if not env_path.exists():
        return
    
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
            os.environ.setdefault(key.strip(), value.strip())


def get_dwh_uri() -> str:
    """Build PostgreSQL connection URI from environment variables."""
    host = os.getenv('DWH_HOST', 'localhost')
    port = os.getenv('DWH_PORT', '5432')
    dbname = os.getenv('DWH_NAME', 'dwh_db')
    user = os.getenv('DWH_USER', 'dwh_user')
    password = os.getenv('DWH_PASS', 'dwh_pass')
    
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"


def refresh_materialized_views(concurrent: bool = True) -> None:
    """
    Refresh all materialized views in the DWH.
    
    Args:
        concurrent: If True, use CONCURRENTLY option (doesn't lock the view)
    """
    views = [
        'mv_monthly_sales',
        'mv_product_performance',
        'mv_regional_performance',
        'mv_customer_performance'
    ]
    
    uri = get_dwh_uri()
    engine = create_engine(uri, echo=False)
    
    print(f"\n{'='*60}")
    print(f"Refreshing Materialized Views - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    total_start = time.time()
    results = []
    
    with engine.connect() as conn:
        for view in views:
            try:
                start_time = time.time()
                print(f"📊 Refreshing {view}...", end=' ', flush=True)
                
                # Use CONCURRENTLY if supported (requires unique index)
                refresh_cmd = f"REFRESH MATERIALIZED VIEW {'CONCURRENTLY' if concurrent else ''} {view}"
                conn.execute(text(refresh_cmd))
                conn.commit()
                
                elapsed = time.time() - start_time
                print(f"✓ Done ({elapsed:.2f}s)")
                results.append((view, 'SUCCESS', elapsed))
                
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"✗ Failed ({elapsed:.2f}s)")
                print(f"   Error: {str(e)}")
                results.append((view, 'FAILED', elapsed))
    
    total_elapsed = time.time() - total_start
    
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")
    
    for view, status, elapsed in results:
        status_icon = '✓' if status == 'SUCCESS' else '✗'
        print(f"{status_icon} {view:30} {status:10} {elapsed:6.2f}s")
    
    print(f"{'='*60}")
    print(f"Total time: {total_elapsed:.2f}s")
    print(f"{'='*60}\n")
    
    # Display view sizes
    print("\n📦 Materialized View Sizes:")
    print(f"{'='*60}")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                  matviewname,
                  pg_size_pretty(pg_total_relation_size('public.' || matviewname)) AS size,
                  n_live_tup AS rows
                FROM pg_matviews
                LEFT JOIN pg_stat_user_tables ON tablename = matviewname
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size('public.' || matviewname) DESC
            """))
            
            for row in result:
                print(f"  {row.matviewname:30} {row.size:>10}  ({row.rows or 0:,} rows)")
    except Exception as e:
        print(f"  Could not fetch sizes: {e}")
    
    print(f"{'='*60}\n")


def main():
    """Main entry point."""
    # Try to load .env file from current directory
    load_env_file()
    
    # Parse command line arguments
    concurrent = '--no-concurrent' not in sys.argv
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        print("\nOptions:")
        print("  --no-concurrent    Refresh without CONCURRENTLY (locks the view)")
        print("  -h, --help         Show this help message")
        return 0
    
    try:
        refresh_materialized_views(concurrent=concurrent)
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
