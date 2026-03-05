"""
Setup.py - Configuration d'installation du package
"""

from setuptools import setup, find_packages

setup(
    name="edpac",
    version="2.0.0",
    description="Event-Driven Pacman - Spiking Neural Network Simulation",
    author="David Meunier",
    author_email="",
    url="https://github.com/davidmeunier79/EDPac",
    license="GPL-3.0",
    
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    python_requires=">=3.8",
    
    install_requires=[
        "numpy>=1.20",
        "scipy>=1.7",
        "matplotlib>=3.3",
        "pandas>=1.3",
    ],
    
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.12",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "visu": ["PySide6","pillow", "pyqtgraph"] # pyside6 conda version not pip # pillow conda also # pyqtgraph conda also
    },

    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
