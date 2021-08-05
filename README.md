# OSS 异步客户端
基于 aiohttp 3.7.4 与 阿里云 OSS 2.15.0 的 OSS 异步客户端

# 安装
虚拟环境中执行
```shell script
$ pip install async-oss
```

# 使用示例

```python
import async_oss
import asyncio
import oss2


OSS_ENDPOINT = 'http://oss-cn-hangzhou.aliyuncs.com'
OSS_KEY = '<Your AccessKeyID>'
OSS_SECRET = '<Your AccessKeySecret>'
OSS_AUTH = oss2.Auth('<Your AccessKeyID>', '<Your AccessKeySecret>')
BUCKET_NAME = '<your bucket name>'
OBJECT_KEY = '<your object key>'


async def main():
    async with async_oss.Bucket(OSS_AUTH, OSS_ENDPOINT, BUCKET_NAME) as bucket:
        # Upload
        await bucket.put_object(OBJECT_KEY, b'your bytes data')

        # Download
        result = await bucket.get_object(OBJECT_KEY)
        await result.read()

        # Delete
        await bucket.delete_object(OBJECT_KEY)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

# ChangeLog
* init 1.0.0
