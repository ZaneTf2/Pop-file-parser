from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pop_file_parser",
    version="0.1.0",
    description="TF2 MvM .pop file compiler and editor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Uncle Zane",
    author_email="demtoreplay@gmail.com",  # Замените на ваш email
    url="https://github.com/ZaneTf2/Pop-file-parser",  # Замените на URL вашего репозитория
    packages=find_packages(),
    install_requires=[
        'click>=7.0',
        'rich>=10.0.0'
    ],
    entry_points={
        'console_scripts': [
            'popcompiler=pop_file_parser.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="tf2, mvm, pop, parser, compiler, team fortress 2, mann vs machine",
    project_urls={
        "Bug Reports": "https://github.com/ZaneTf2/Pop-file-parser/issues",
        "Documentation": "https://github.com/ZaneTf2/Pop-file-parser#readme",
    },
)
