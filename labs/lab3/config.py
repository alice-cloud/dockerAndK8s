import os


class Config(object):
    REDIS_URL = "redis://{}:6379/0".format(os.environ.get("REDIS_SERVER"))
