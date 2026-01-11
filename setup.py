from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="stock-pattern-matcher",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="株価・FXのローソク足パターンマッチングシステム",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stock-pattern-matcher",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/stock-pattern-matcher/issues",
        "Documentation": "https://github.com/yourusername/stock-pattern-matcher/docs",
        "Source Code": "https://github.com/yourusername/stock-pattern-matcher",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "sphinx>=4.0.0",
        ],
        "ml": [
            "scikit-learn>=1.0.0",
            "tensorflow>=2.8.0",
            "torch>=1.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pattern-matcher=stock_pattern_matcher.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "stock_pattern_matcher": ["data/*.csv"],
    },
)
