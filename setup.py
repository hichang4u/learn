from setuptools import setup, find_packages

setup(
    name='LEARN',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
    ],
    entry_points={
        'console_scripts': [
            'learn=app.main:app',
        ],
    },
) 