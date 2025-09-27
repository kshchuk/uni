from setuptools import setup, find_packages

setup(
    name="lab-gd",
    version="0.1.0",
    description="Gradient descent experimentation toolkit for Variant 9 objective",
    packages=find_packages(include=["lab_gd", "lab_gd.*"]),
    install_requires=[
        "numpy",
        "plotly",
        "ipywidgets",
        "matplotlib",
    ],
)
