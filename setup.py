#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='async-oss',
    version='1.0.0',
    description='An asynchronous OSS library based on OSS2=2.15.0.',
    author='longyao',
    author_email='longyao@91jkys.com',
    license='MIT',
    install_requires=['aiohttp', 'oss2'],
    packages=find_packages(),
)
