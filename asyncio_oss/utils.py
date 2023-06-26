# -*- coding: utf-8 -*-

"""
oss2.utils
----------

工具函数模块。
"""
import logging

from .exceptions import ClientError

from oss2.compat import to_bytes
from oss2.utils import (Crc64, _IterableAdapter, _get_data_size, _has_data_size_attr, _CHUNK_SIZE,
                        _invoke_cipher_callback, _invoke_crc_callback, _invoke_progress_callback)


logger = logging.getLogger(__name__)


def make_crc_adapter(data, init_crc=0, discard=0):
    """返回一个适配器，从而在读取 `data` ，即调用read或者对其进行迭代的时候，能够计算CRC。

    :param discard:
    :return:
    :param data: 可以是bytes、file object或iterable
    :param init_crc: 初始CRC值，可选

    :return: 能够调用计算CRC函数的适配器
    """
    data = to_bytes(data)

    # bytes or file object
    if _has_data_size_attr(data):
        if discard:
            raise ClientError('Bytes of file object adapter does not support discard bytes')
        return _BytesAndFileAdapter(data, size=_get_data_size(data), crc_callback=Crc64(init_crc))
    # file-like object
    elif hasattr(data, 'read'):
        return _FileLikeAdapter(data, crc_callback=Crc64(init_crc), discard=discard)
    # iterator
    elif hasattr(data, '__iter__'):
        if discard:
            raise ClientError('Iterator adapter does not support discard bytes')
        return _IterableAdapter(data, crc_callback=Crc64(init_crc))
    else:
        raise ClientError('{0} is not a file object, nor an iterator'.format(data.__class__.__name__))


class _FileLikeAdapter(object):
    """通过这个适配器，可以给无法确定内容长度的 `fileobj` 加上进度监控。

    :param fileobj: file-like object，只要支持read即可
    :param progress_callback: 进度回调函数
    """

    def __init__(self, fileobj, progress_callback=None, crc_callback=None, cipher_callback=None, discard=0):
        self.fileobj = fileobj
        self.progress_callback = progress_callback
        self.offset = 0

        self.crc_callback = crc_callback
        self.cipher_callback = cipher_callback
        self.discard = discard
        self.read_all = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.anext()

    async def anext(self):
        if self.read_all:
            raise StopIteration

        content = await self.read(_CHUNK_SIZE)

        if content:
            return content
        else:
            raise StopIteration

    async def read(self, amt=None):
        offset_start = self.offset
        if offset_start < self.discard and amt and self.cipher_callback:
            amt += self.discard

        content = await self.fileobj.read(amt)
        if not content:
            self.read_all = True
            _invoke_progress_callback(self.progress_callback, self.offset, None)
        else:
            _invoke_progress_callback(self.progress_callback, self.offset, None)

            self.offset += len(content)

            real_discard = 0
            if offset_start < self.discard:
                if len(content) <= self.discard:
                    real_discard = len(content)
                else:
                    real_discard = self.discard

            _invoke_crc_callback(self.crc_callback, content, real_discard)
            content = _invoke_cipher_callback(self.cipher_callback, content, real_discard)

            self.discard -= real_discard
        return content

    @property
    def crc(self):
        if self.crc_callback:
            return self.crc_callback.crc
        elif self.fileobj:
            return self.fileobj.crc
        else:
            return None


class _BytesAndFileAdapter(object):
    """通过这个适配器，可以给 `data` 加上进度监控。

    :param data: 可以是unicode字符串（内部会转换为UTF-8编码的bytes）、bytes或file object
    :param progress_callback: 用户提供的进度报告回调，形如 callback(bytes_read, total_bytes)。
        其中bytes_read是已经读取的字节数；total_bytes是总的字节数。
    :param int size: `data` 包含的字节数。
    """

    def __init__(self, data, progress_callback=None, size=None, crc_callback=None, cipher_callback=None):
        self.data = to_bytes(data)
        self.progress_callback = progress_callback
        self.size = size
        self.offset = 0

        self.crc_callback = crc_callback
        self.cipher_callback = cipher_callback

    @property
    def len(self):
        return self.size

    # for python 2.x
    def __bool__(self):
        return True

    # for python 3.x
    __nonzero__ = __bool__

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.next()

    async def next(self):
        content = await self.read(_CHUNK_SIZE)

        if content:
            return content
        else:
            raise StopIteration

    async def read(self, amt=None):
        if self.offset >= self.size:
            return to_bytes('')

        if amt is None or amt < 0:
            bytes_to_read = self.size - self.offset
        else:
            bytes_to_read = min(amt, self.size - self.offset)

        if isinstance(self.data, bytes):
            content = self.data[self.offset:self.offset + bytes_to_read]
        else:
            content = await self.data.read(bytes_to_read)

        self.offset += bytes_to_read

        _invoke_progress_callback(self.progress_callback, min(self.offset, self.size), self.size)

        _invoke_crc_callback(self.crc_callback, content)

        content = _invoke_cipher_callback(self.cipher_callback, content)

        return content

    @property
    def crc(self):
        if self.crc_callback:
            return self.crc_callback.crc
        elif self.data:
            return self.data.crc
        else:
            return None

