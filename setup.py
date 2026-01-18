#!/usr/bin/env python3
"""
Setup script for Chore CLI
"""

from setuptools import setup, find_packages

setup(
    name="chore-cli",
    version="1.0.0",
    description="Chore management system with TMUX integration",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'chore=chore_dispatcher.chore_enhanced:main',
        ],
    },
    python_requires='>=3.7',
    install_requires=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7+",
    ],
)
