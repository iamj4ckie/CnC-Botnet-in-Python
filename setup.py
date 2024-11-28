from setuptools import setup, find_packages

## script added to make the project installable as a Python package.

setup(
    name="botnet-cli",
    version="1.0.0",
    packages=find_packages(),
    py_modules=["botnet_cli"], 
    install_requires=[],
    entry_points={
        'console_scripts': [
            'botnet-cli=botnet_cli:main', 
        ],
    },
    description="CLI for botnet",
)
