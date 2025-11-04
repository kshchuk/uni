"""
Setup script для TechMarket ETL пакету.

Використання:
    pip install -e .
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='techmarket-etl',
    version='1.0.0',
    author='Yaroslav Kischuk',
    author_email='yaroslav.kischuk@student.uzhnu.edu.ua',
    description='ETL pipeline для TechMarket Data Warehouse',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kshchuk/uni',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.12',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.7.0',
        ],
        'airflow': [
            'apache-airflow>=2.7.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'techmarket-etl=etl.run_etl:main',
        ],
    },
    include_package_data=True,
    package_data={
        'etl': ['*.md', '*.txt', '*.example'],
    },
)
