# 阿里云 OSS 异步客户端 (Aliyun OSS asynchronous client)
基于 aiohttp 与 阿里云 OSS 的 OSS 异步客户端。</br>
已在 QPS ≈ 500 的生产环境中验证使用并平稳落地，可放心使用。</br>
Based on aiohttp==3.7.4 & oss==2.15.0.</br>
It has been verified and used in the production environment with QPS ≈ 500, so you can use it with confidence.</br>

# 安装 (Installation)
## PyPI (recommend)
```shell script
$ pip install asyncio-oss
```

## 本地编译 (Local compilation)
git clone 到本地后执行如下命令即可。</br>
After clone to local, execute the following commands in the virtual environment.
```shell script
$ python setup.py bdist_wheel

$ pip install ./dist/asyncio_oss-1.0.0-py3-none-any.whl
```

# 使用示例 (Example)

```python
import asyncio_oss
import asyncio
import oss2

OSS_ENDPOINT = 'http://oss-cn-hangzhou.aliyuncs.com'
OSS_KEY = '<Your AccessKeyID>'
OSS_SECRET = '<Your AccessKeySecret>'
OSS_AUTH = oss2.Auth(OSS_KEY, OSS_SECRET)
BUCKET_NAME = '<your bucket name>'
OBJECT_KEY = '<your object key>'


async def main():
    async with asyncio_oss.Bucket(OSS_AUTH, OSS_ENDPOINT, BUCKET_NAME) as bucket:
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
* fix `http.py/do_request` method stream read  [Jul 29, 2022]


# Discussions
Any questions can be raised in Discussions, I will answer them from time to time~
