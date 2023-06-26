# -*- coding: utf-8 -*-

"""
oss2.models
~~~~~~~~~~

该模块包含Python SDK API接口所需要的输入参数以及返回值类型。
"""
import logging
import copy

from .exceptions import ClientError
from .utils import make_crc_adapter

from oss2.utils import make_progress_adapter
from oss2.headers import *
from oss2.models import HeadObjectResult, ContentCryptoMaterial, _hget, KMS_ALI_WRAP_ALGORITHM

logger = logging.getLogger(__name__)


class GetObjectResult(HeadObjectResult):
    def __init__(self, resp, progress_callback=None, crc_enabled=False, crypto_provider=None, discard=0):
        super(GetObjectResult, self).__init__(resp)
        self.__crc_enabled = crc_enabled
        self.__crypto_provider = crypto_provider

        self.content_range = _hget(resp.headers, 'Content-Range')
        if self.content_range:
            byte_range = self._parse_range_str(self.content_range)

        if progress_callback:
            self.stream = make_progress_adapter(self.resp, progress_callback, self.content_length)
        else:
            self.stream = self.resp

        if self.__crc_enabled:
            self.stream = make_crc_adapter(self.stream, discard=discard)

        if self.__crypto_provider:
            content_crypto_material = ContentCryptoMaterial(self.__crypto_provider.cipher,
                                                            self.__crypto_provider.wrap_alg)
            content_crypto_material.from_object_meta(resp.headers)

            if content_crypto_material.is_unencrypted():
                logger.info("The object is not encrypted, use crypto provider is not recommended")
            else:
                crypto_provider = self.__crypto_provider
                if content_crypto_material.mat_desc != self.__crypto_provider.mat_desc:
                    logger.warn("The material description of the object and the provider is inconsistent")
                    encryption_materials = self.__crypto_provider.get_encryption_materials(
                        content_crypto_material.mat_desc)
                    if encryption_materials:
                        crypto_provider = self.__crypto_provider.reset_encryption_materials(encryption_materials)
                    else:
                        raise ClientError(
                            'There is no encryption materials match the material description of the object')

                plain_key = crypto_provider.decrypt_encrypted_key(content_crypto_material.encrypted_key)
                if content_crypto_material.deprecated:
                    if content_crypto_material.wrap_alg == KMS_ALI_WRAP_ALGORITHM:
                        plain_counter = int(
                            crypto_provider.decrypt_encrypted_iv(content_crypto_material.encrypted_iv, True))
                    else:
                        plain_counter = int(crypto_provider.decrypt_encrypted_iv(content_crypto_material.encrypted_iv))
                else:
                    plain_iv = crypto_provider.decrypt_encrypted_iv(content_crypto_material.encrypted_iv)

                offset = 0
                if self.content_range:
                    start, end = crypto_provider.adjust_range(byte_range[0], byte_range[1])
                    offset = content_crypto_material.cipher.calc_offset(start)

                cipher = copy.copy(content_crypto_material.cipher)
                if content_crypto_material.deprecated:
                    cipher.initial_by_counter(plain_key, plain_counter + offset)
                else:
                    cipher.initialize(plain_key, plain_iv, offset)
                self.stream = crypto_provider.make_decrypt_adapter(self.stream, cipher, discard)
        else:
            if OSS_CLIENT_SIDE_ENCRYPTION_KEY in resp.headers or DEPRECATED_CLIENT_SIDE_ENCRYPTION_KEY in resp.headers:
                logger.warn(
                    "Using Bucket to get an encrypted object will return raw data, please confirm if you really want to do this")

    @staticmethod
    def _parse_range_str(content_range):
        # :param str content_range: sample 'bytes 0-128/1024'
        range_data = (content_range.split(' ', 2)[1]).split('/', 2)[0]
        range_start, range_end = range_data.split('-', 2)
        return int(range_start), int(range_end)

    def read(self, amt=None):
        return self.stream.read(amt)

    def close(self):
        self.resp.response.close()

    def __iter__(self):
        return iter(self.stream)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def client_crc(self):
        if self.__crc_enabled:
            return self.stream.crc
        else:
            return None
