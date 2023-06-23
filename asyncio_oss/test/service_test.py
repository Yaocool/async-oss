import pytest

from asyncio_oss.api import Service
from asyncio_oss.test import (OSS_ENDPOINT, OSS_AUTH, BUCKET_NAME)


class TestAsyncOssServiceAPI:
    @pytest.fixture
    def api(self):
        return Service(OSS_AUTH, OSS_ENDPOINT)

    @pytest.mark.asyncio
    async def test_list_buckets(self, api):
        # Act
        result = await api.list_buckets()

        # Assert
        assert result.status == 200
        assert BUCKET_NAME in [bucket_info.name for bucket_info in result.buckets]
