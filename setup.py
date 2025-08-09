#!/usr/bin/env python3
"""
Setup script for Flight Data Analysis Package
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="flight-data-analysis",
    version="1.0.0",
    author="Flight Data Analysis Team",
    author_email="team@flightanalysis.com",
    description="A comprehensive tool for analyzing Indian domestic airlines flight data",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Flight_data_log",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "flight-analysis=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
    keywords="data-analysis, airlines, flight-data, visualization, dashboard, python",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/Flight_data_log/issues",
        "Source": "https://github.com/yourusername/Flight_data_log",
        "Documentation": "https://github.com/yourusername/Flight_data_log/docs",
    },
) 