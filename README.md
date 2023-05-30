# An asynchronous python client SDK for OSS(Aliyun Object Storage Service).
It has been verified and used in the production environment with QPS ≈ 500  for about half a year, so you can use it with confidence.

# Installation
## PyPI (recommend)
```shell script
$ pip install asyncio-oss
```

## Local compilation
```shell script
$ git clone git@github.com:Yaocool/async-oss.git
$ python setup.py bdist_wheel
$ pip install ./dist/asyncio_oss-1.0.0-py3-none-any.whl
```

# Example
```python
import asyncio_oss
import asyncio
import oss2

OSS_ENDPOINT = 'https://oss-cn-hangzhou.aliyuncs.com'  # definition in https://help.aliyun.com/document_detail/31837.html
OSS_KEY = '<Your AccessKeyID>'
OSS_SECRET = '<Your AccessKeySecret>'
OSS_AUTH = oss2.Auth(OSS_KEY, OSS_SECRET)
BUCKET_NAME = '<your bucket name>'
OBJECT_KEY = '<your object key>'


async def main():
    async with asyncio_oss.Bucket(OSS_AUTH, OSS_ENDPOINT, BUCKET_NAME) as bucket:
        # Put Object
        await bucket.put_object(OBJECT_KEY, b'your bytes data')

        # Get Object
        result = await bucket.get_object(OBJECT_KEY)
        await result.read()
        
        # Head Object
        head_res = await bucket.head_object(OBJECT_KEY)
        print(head_res.content_length)
        
        # List Objects
        for obj in (await bucket.list_objects()).object_list:
            print(obj.key)

        # Delete Object
        await bucket.delete_object(OBJECT_KEY)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

# ChangeLogs
* init 1.0.0
* [Jul 29, 2022] fix `http.py/do_request` method stream read bug
* [May 29, 2023] add test cases and supported `asyncio-oss` package in PyPI


# Discussions
Any questions can be raised in Discussions, I will answer them from time to time~
