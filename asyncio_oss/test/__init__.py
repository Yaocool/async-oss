import os

import oss2

OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT')
OSS_KEY = os.environ.get('OSS_KEY')
OSS_SECRET = os.environ.get('OSS_SECRET')
BUCKET_NAME = os.environ.get('OSS_BUCKET')
OBJECT_KEY = os.environ.get('OSS_OBJECT_KEY')
BIG_OBJECT_KEY = os.environ.get('OSS_BIG_OBJECT_KEY')
OBJECT_KEY_PREFIX = os.environ.get('OSS_OBJECT_KEY_PREFIX')
LOCAL_TEST_FILE = 'test.txt'
LOCAL_TEST_BIG_FILE = 'test_big.txt'
OSS_AUTH = oss2.Auth(OSS_KEY, OSS_SECRET)

if __name__ == '__main__':
    for i in [OSS_KEY, OSS_SECRET, BUCKET_NAME, OBJECT_KEY, OBJECT_KEY_PREFIX, LOCAL_TEST_FILE]:
        assert i is not None
        assert i != ""
