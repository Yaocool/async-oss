#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='async-oss',
    version='1.0.0',
    description='An asynchronous OSS library.',
    author='Ozzy',
    author_email='ozzycharon@gmail.com',
    license='MIT',
    install_requires=['aiohttp', 'oss2'],
    packages=find_packages(),
)
