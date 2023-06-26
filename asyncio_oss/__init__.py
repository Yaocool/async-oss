from oss2 import set_file_logger as oss_set_file_logger, set_stream_logger as oss_set_stream_logger
from oss2.auth import Auth

from .api import Service, Bucket
from .iterators import (
    BucketIterator,
    ObjectIterator,
    ObjectIteratorV2,
    MultipartUploadIterator,
    ObjectUploadIterator,
    PartIterator, LiveChannelIterator)

import logging

__all__ = [
    'Auth', 'Service', 'Bucket', 'BucketIterator',
    'ObjectIterator',
    'MultipartUploadIterator',
    'ObjectUploadIterator',
    'PartIterator',
    'LiveChannelIterator'
]


def set_file_logger(file_path, name='asyncio_oss', level=logging.INFO, format_string=None):
    oss_set_file_logger(file_path, name, level, format_string)


def set_stream_logger(name='asyncio_oss', level=logging.DEBUG, format_string=None):
    oss_set_stream_logger(name, level, format_string)
