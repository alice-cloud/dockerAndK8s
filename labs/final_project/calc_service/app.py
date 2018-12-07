import os
import sys
import time

import tornado.ioloop
import tornado.options
import tornado.web

import redis

import pika
from pika.adapters.tornado_connection import TornadoConnection

import pickle
import logging

from tornado.options import define, options


define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        self.recieve = CaculateWorker()
        self.recieve.connect()

        handlers = []
        settings = dict(
            cookie_secret="UXZpTuZvFACo1pOgNNvG0sbPm4RFyNToXzI+HAtkp4c=",
            xsrf_cookies=True,
        )
        super(Application, self).__init__(handlers, **settings)


class CaculateWorker(object):
    REDIS_HASHMAP_KEY = os.environ.get("REDIS_HASHMAP_KEY")

    def __init__(self):
        rabbitmq_server = os.environ.get("RABBITMQ_SERVER")
        redis_server = os.environ.get("REDIS_SERVER")
        redis_port = 6379

        self.redis_client = redis.Redis(host=redis_server, port=redis_port, db=0)

        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.connection = None
        self.channel = None

        self._delivery_tag = 0

        self.parameters = pika.ConnectionParameters(rabbitmq_server)

    @staticmethod
    def fibonacci(index):
        if index <= 1:
            return 1
        return CaculateWorker.fibonacci(index - 1) + CaculateWorker.fibonacci(index - 2)

    def cache_cacalate(self, index, value):
        self.redis_client.hset(CaculateWorker.REDIS_HASHMAP_KEY, index, value)

    def connect(self):
        try:
            self.connection = TornadoConnection(self.parameters, on_open_callback=self.on_connected, stop_ioloop_on_close=False, on_open_error_callback=self.on_open_error)
            self.connection.add_on_close_callback(self.on_closed)
        except:
            logging.info("connect faield")

    def on_open_error(self, unused_connection, err):
        sys.exit(1)

    def on_connected(self, connection):
        logging.info('PikaClient: connected to RabbitMQ')
        self.connection.channel(self.on_exchange_declare)

    def on_exchange_declare(self, channel):
        logging.info('PikaClient: Channel %s open, Declaring exchange' % channel)
        self.channel = channel
        self.channel.exchange_declare(self.on_queue_declare, exchange='calc_fibonacci', exchange_type='direct')
        self.channel.exchange_declare(self.on_queue_declare, exchange='notification', exchange_type='direct')

    def on_queue_declare(self, method_frame):
        logging.info('PikaClient: Channel open, Declaring queue')
        self.channel.queue_declare(self.on_queue_bind, queue='calc_fibonacci') #, durable=True)
        self.channel.queue_declare(self.on_queue_bind, queue='notification') #, durable=True)

    def on_queue_bind(self, method_frame):
        logging.info('Queue bound')
        self.channel.queue_bind(self.on_consume_bind, queue="calc_fibonacci", exchange="calc_fibonacci", routing_key="calc_fibonacci")
        self.channel.queue_bind(self.on_consume_bind, queue="notification", exchange="notification", routing_key="notification")

    def on_consume_bind(self, frame):
        logging.info("Consume bind")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_response, queue='calc_fibonacci', no_ack=False)

    def on_response(self, channel, method, properties, body):
        logging.info('on_response')
        message=pickle.loads(body)
        logging.info(message)
        
        uuid, index = message['uuid'], message['index']
        value = CaculateWorker.fibonacci(index)
        self.cache_cacalate(index, value)

        result = {
            'id': uuid,
            'index': index,
            'value': value,
        }
        logging.info(result)

        channel.basic_publish(exchange='notification', routing_key='notification', body=pickle.dumps(result))
        logging.info("publish done")
        channel.basic_ack(delivery_tag = method.delivery_tag)

    def on_closed(self, connection):
        logging.info('PikaClient: rabbit connection closed')
        self.connection.close()
        self.channel.close()
        self.ioloop.stop()


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()