# -*- coding: utf-8 -*-

"""
oss2.http
~~~~~~~~

这个模块包含了HTTP Adapters。尽管OSS Python SDK内部使用requests库进行HTTP通信，但是对使用者是透明的。
该模块中的 `Session` 、 `Request` 、`Response` 对requests的对应的类做了简单的封装。
"""
import logging
import platform

from .exceptions import RequestError

import aiohttp
from requests.structures import CaseInsensitiveDict

from oss2 import __version__, defaults
from oss2.compat import to_bytes
from oss2.utils import file_object_remaining_bytes, SizedFileAdapter

USER_AGENT = 'aliyun-sdk-python/{0}({1}/{2}/{3};{4})'.format(
    __version__, platform.system(), platform.release(), platform.machine(), platform.python_version())

logger = logging.getLogger(__name__)


class Session(object):
    """属于同一个Session的请求共享一组连接池，如有可能也会重用HTTP连接。"""

    def __init__(self):
        self.resp = None
        self._aio_session = None

    async def _create_session(self):
        if self._aio_session is None:
            pool_size = defaults.connection_pool_size
            connector = aiohttp.TCPConnector(limit=pool_size)
            self._aio_session = aiohttp.ClientSession(connector=connector)

    async def do_request(self, req, timeout):
        try:
            logger.debug(
                "Send request, method: {0}, url: {1}, params: {2}, headers: {3}, timeout: {4}, proxies: {5}".format(
                    req.method, req.url, req.params, req.headers, timeout, req.proxies))

            await self._create_session()
            # 1. When setting progress_callback or enabling crc verification, the data type will be converted to the
            # corresponding adapter object by oss make_progress_adapter / make_crc_adapter, and the process_callback
            # and crc verification calculation will be performed when read
            # 2. requests supports the reading of file-like-objects, while aiohttp does not, so you need to read the
            # data in advance
            req_data = req.data.read() if hasattr(req.data, 'read') else req.data
            resp = await self._aio_session.request(
                req.method,
                req.url,
                data=req_data,
                params=req.params,
                headers=req.headers,
                timeout=timeout,
                proxy=req.proxies
            )
            self.resp = resp
            return Response(resp)
        except IOError as e:
            # catch read IO error
            raise RequestError(e)
        except aiohttp.ClientError as e:
            # catch all aiohttp client errors
            await self._aio_session.close()
            raise RequestError(e)

    async def __aenter__(self):
        await self._create_session()
        await self._aio_session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._aio_session.__aexit__(exc_type, exc_val, exc_tb)


class Request(object):
    def __init__(self, method, url,
                 data=None,
                 params=None,
                 headers=None,
                 app_name='',
                 proxies=None,
                 region=None,
                 product=None,
                 cloudbox_id=None):
        self.method = method
        self.url = url
        self.data = _convert_request_body(data)
        self.params = params or {}
        self.proxies = proxies
        self.region = region
        self.product = product
        self.cloudbox_id = cloudbox_id

        if not isinstance(headers, CaseInsensitiveDict):
            self.headers = CaseInsensitiveDict(headers)
        else:
            self.headers = headers

        # tell aiohttp not to add 'Content-Type: application/octet-stream' by default
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = ''

        if 'User-Agent' not in self.headers:
            if app_name:
                self.headers['User-Agent'] = USER_AGENT + '/' + app_name
            else:
                self.headers['User-Agent'] = USER_AGENT

        logger.debug("Init request, method: {0}, url: {1}, params: {2}, headers: {3}".format(method, url, params,
                                                                                             headers))


_CHUNK_SIZE = 8 * 1024


class Response(object):
    def __init__(self, response):
        self.response = response
        self.status = response.status
        self.headers = response.headers
        self.request_id = response.headers.get('x-oss-request-id', '')

        # When a response contains no body, iter_content() cannot
        # be run twice (requests.exceptions.StreamConsumedError will be raised).
        # For details of the issue, please see issue #82
        #
        # To work around this issue, we simply return b'' when everything has been read.
        #
        # Note you cannot use self.response.raw.read() to implement self.read(), because
        # raw.read() does not uncompress response body when the encoding is gzip etc., and
        # we try to avoid depends on details of self.response.raw.
        self.__all_read = False

        logger.debug("Get response headers, req-id:{0}, status: {1}, headers: {2}".format(self.request_id, self.status,
                                                                                          self.headers))

    async def read(self, amt=None):
        if self.__all_read:
            return b''

        if amt is None:
            content_list = []
            async for chunk in self.response.content.iter_chunked(_CHUNK_SIZE):
                content_list.append(chunk)
            content = b''.join(content_list)

            self.__all_read = True
            return content
        else:
            try:
                return await self.response.content.read(amt)
            except StopAsyncIteration:
                self.__all_read = True
                return b''

    def __aiter__(self):
        return self.response.content


# requests 对于具有 fileno() 方法的 file object，会用 fileno() 的返回值作为 Content-Length。
# 这对于已经读取了部分内容，或执行了seek() 的 file object是不正确的。
#
# _convert_request_body() 对于支持 seek() 和 tell() file object，确保是从
# 当前位置读取，且只读取当前位置到文件结束的内容。
def _convert_request_body(data):
    data = to_bytes(data)

    if hasattr(data, '__len__'):
        return data

    if hasattr(data, 'seek') and hasattr(data, 'tell'):
        return SizedFileAdapter(data, file_object_remaining_bytes(data))

    return data
