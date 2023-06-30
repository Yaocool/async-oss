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
$ pip install ./dist/asyncio_oss-1.1.1-py3-none-any.whl
```

# Examples
For more examples, please refer to the [test](./asyncio_oss/test) directory.
```python
import logging

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
    # open global log
    log_file_path = "example_logfile.log"
    asyncio_oss.set_file_logger(log_file_path, 'asyncio_oss', logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

# ChangeLogs
* [Jul 29, 2022 - 1.0.0]
  * fix `http.py/do_request` method stream read bug


* [May 29, 2023]
  * add test cases and supported `asyncio-oss` package in PyPI


* [May 30, 2023 - 1.0.1]
  * bump version to 1.0.1 for PyPI package description updating


* [June 24, 2023 - 1.0.2]
  * remove unused fields add params in `asyncio_oss/http.py api.py` files
  * fix `asyncio_oss/iterators.py/_BaseIterator/__aiter__` method bug
  * add `list_buckets` test case in `tests/service_test.py` for `Service` class
  * bump version to 1.0.2


* [June 27, 2023 - 1.1.0]
  * remove unused objects and methods in `asyncio_oss/models.py` and `asyncio_oss/utils.py` to streamline sdk package
  * support oss2==2.18.0 newest apis
  * support global log
  * bump version to 1.1.0


* [June 28, 2023 - 1.1.1]
  * fix the bug of wrong signature of `put_object_tagging` interface caused by default `Content-Type` of aiohttp
  * bump version to 1.1.1

# Discussions Or Issues
Any questions can be raised in `Discussions` or `Issues`, I will answer them from time to time.
