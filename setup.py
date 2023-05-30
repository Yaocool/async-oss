#!/usr/bin/env python
import pathlib

from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='asyncio-oss',
    version='1.0.1',
    description='An asynchronous python client SDK for OSS(Aliyun Object Storage Service).',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yaocool/async-oss",
    keywords="asyncio-oss, async-oss, oss",
    author='Ozzy',
    author_email='ozzycharon@gmail.com',
    license='MIT',
    install_requires=['aiohttp', 'oss2'],
    packages=find_packages(),
)
