# setup.py
from setuptools import setup, find_packages

setup(
    name="financial-news-sentiment-analysis",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
