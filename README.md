# OSS 异步客户端 (OSS async client)
基于 aiohttp 3.7.4 与 阿里云 OSS 2.15.0 的 OSS 异步客户端。</br>
Based on aiohttp==3.7.4 & oss==2.15.0.

# 安装 (Installation)
clone 到本地后使用 Pyinstaller 打包成 wheel 包，在虚拟环境中执行以下命令即可。</br>
After clone to local, use Pyinstaller to package the wheel package and execute the following command in the virtual environment.
```shell script
$ pip install async-oss
```

# 使用示例 (Example)

```python
import async_oss
import asyncio
import oss2


OSS_ENDPOINT = 'http://oss-cn-hangzhou.aliyuncs.com'
OSS_KEY = '<Your AccessKeyID>'
OSS_SECRET = '<Your AccessKeySecret>'
OSS_AUTH = oss2.Auth(OSS_KEY, OSS_SECRET)
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
