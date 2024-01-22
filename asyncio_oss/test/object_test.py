import asyncio
import os

import pytest

from oss2 import determine_part_size, SizedFileAdapter
from oss2.models import PartInfo

from asyncio_oss.api import Bucket
from asyncio_oss.test import (OSS_ENDPOINT, OSS_AUTH, BUCKET_NAME, OBJECT_KEY, OBJECT_KEY_PREFIX, LOCAL_TEST_FILE,
                              LOCAL_TEST_BIG_FILE, BIG_OBJECT_KEY)


class TestAsyncOssAPI:
    @pytest.fixture
    def api(self):
        bucket = Bucket(OSS_AUTH, OSS_ENDPOINT, BUCKET_NAME)
        yield bucket
        asyncio.run(bucket.close())

    @pytest.mark.asyncio
    async def test_put_object(self, api):
        # Arrange
        with open(LOCAL_TEST_FILE, 'rb') as f:
            data = f.read()

        # Act
        result = await api.put_object(OBJECT_KEY, data)

        # Assert
        assert result.status == 200

    @pytest.mark.asyncio
    async def test_put_object_with_tagging(self, api):
        from oss2.headers import OSS_OBJECT_TAGGING

        # Arrange
        with open(LOCAL_TEST_FILE, 'rb') as f:
            data = f.read()

        # Act
        tagging = "k1=v1"
        headers = {OSS_OBJECT_TAGGING: tagging}

        result = await api.put_object(OBJECT_KEY, data, headers=headers)

        # Assert
        assert result.status == 200
        res = await api.get_object_tagging(OBJECT_KEY)
        assert res.status == 200
        assert res.tag_set.tagging_rule.get('k1', '') == 'v1'

    @pytest.mark.asyncio
    async def test_put_object_from_file(self, api):
        # Act
        result = await api.put_object_from_file(OBJECT_KEY, LOCAL_TEST_FILE)

        # Assert
        assert result.status == 200

    @pytest.mark.asyncio
    async def test_get_object(self, api):
        # Act
        result = await api.get_object(OBJECT_KEY)

        # Assert
        assert result.status == 200
        with open(LOCAL_TEST_FILE, 'rb') as f:
            assert await result.read() == f.read()

    @pytest.mark.asyncio
    async def test_list_objects(self, api):
        # Act
        result = await api.list_objects(prefix=OBJECT_KEY_PREFIX)

        # Assert
        assert result.status == 200
        assert OBJECT_KEY in [obj.key for obj in result.object_list]

    @pytest.mark.asyncio
    async def test_list_objects_v2(self, api):
        # Act
        result = await api.list_objects_v2(prefix=OBJECT_KEY_PREFIX)

        # Assert
        assert result.status == 200
        assert OBJECT_KEY in [obj.key for obj in result.object_list]

    @pytest.mark.asyncio
    async def test_head_object(self, api):
        # Act
        result = await api.head_object(OBJECT_KEY)

        # Assert
        assert result.status == 200
        with open(LOCAL_TEST_FILE, 'rb') as f:
            data_length = len(f.read())
        assert result.content_length == data_length

    @pytest.mark.asyncio
    async def test_put_object_tagging(self, api):
        from oss2.models import TaggingRule, Tagging

        # Act
        rule = TaggingRule()
        rule.add('key1', 'value1')

        # 创建标签。
        tagging = Tagging(rule)

        result = await api.put_object_tagging(OBJECT_KEY, tagging)

        # Assert
        assert result.status == 200

    @pytest.mark.asyncio
    async def test_get_object_tagging(self, api):
        # Act
        result = await api.get_object_tagging(OBJECT_KEY)

        # Assert
        assert result.status == 200
        assert result.tag_set.tagging_rule.get('key1', '') == 'value1'

    @pytest.mark.asyncio
    async def test_sign_url(self, api):
        # Act
        result = await api.sign_url('GET', OBJECT_KEY, 5 * 60)
        assert result is not None
        assert result != ""

    @pytest.mark.asyncio
    async def test_delete_object(self, api):
        # Act
        result = await api.delete_object(OBJECT_KEY)

        # Assert
        assert result.status == 204

        # Assert
        result = await api.list_objects(prefix=OBJECT_KEY_PREFIX)
        assert result.status == 200
        assert OBJECT_KEY not in [obj.key for obj in result.object_list]

    @pytest.mark.asyncio
    async def test_upload_big_file(self, api):
        # get big file total size
        total_size = os.path.getsize(LOCAL_TEST_BIG_FILE)

        # determine part size
        part_size = determine_part_size(total_size)

        # init multipart upload
        upload_id = (await api.init_multipart_upload(BIG_OBJECT_KEY)).upload_id

        # upload parts
        parts = []
        with open(LOCAL_TEST_BIG_FILE, 'rb') as f:
            part_number = 1
            offset = 0
            while offset < total_size:
                num_to_upload = min(part_size, total_size - offset)
                result = await api.upload_part(BIG_OBJECT_KEY, upload_id, part_number,
                                               SizedFileAdapter(f, num_to_upload))
                parts.append(PartInfo(part_number, result.etag))

                offset += num_to_upload
                part_number += 1

        # complete multipart upload
        await api.complete_multipart_upload(BIG_OBJECT_KEY, upload_id, parts)

        # Assert
        with open(LOCAL_TEST_BIG_FILE, 'rb') as f:
            assert await (await api.get_object(BIG_OBJECT_KEY)).read() == f.read()

    @pytest.mark.asyncio
    async def test_get_object_to_file(self, api):
        result = await api.get_object_to_file(OBJECT_KEY, LOCAL_TEST_FILE)
        assert result.status == 200
        with open(LOCAL_TEST_FILE, "rb") as f:
            assert f.read() == b"test"
    
    @pytest.mark.asyncio
    async def test_get_object_with_url_to_file(self, api):
        url = await api.sign_url('GET', OBJECT_KEY, 5 * 60)
        result = await api.get_object_with_url_to_file(url, LOCAL_TEST_FILE)
        assert result.status == 200
        with open(LOCAL_TEST_FILE, "rb") as f:
            assert f.read() == b"test"
