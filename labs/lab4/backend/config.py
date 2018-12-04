import os


class Config(object):
    REDIS_URL = "redis://{}:6379/0".format(os.environ.get("REDIS_SERVER"))
    SECRET_KEY = 'oh_so_secret'
    FLASK_PIKA_PARAMS = {
        'host':'amqp',      #amqp.server.com
        'username': 'guest',  #convenience param for username
        'password': 'guest',  #convenience param for password
        'port': 5672,            #amqp server port
        'virtual_host':'vhost'   #amqp vhost
    }
