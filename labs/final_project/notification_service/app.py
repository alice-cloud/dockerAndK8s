import sys
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import pika
from pika.adapters.tornado_connection import TornadoConnection
import pickle
import json
import uuid
import logging
import os

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

rabbitmq_server = os.environ.get("RABBITMQ_SERVER")

class Application(tornado.web.Application):
    def __init__(self):
        self.recieve = PikaClient()
        self.recieve.connect()

        handlers = [(r"/notification", ChatSocketHandler)]
        settings = dict(
            cookie_secret="UXZpTuZvFACo1pOgNNvG0sbPm4RFyNToXzI+HAtkp4c=",
            xsrf_cookies=True,
        )
        super(Application, self).__init__(handlers, **settings)


class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = {}
 
    def check_origin(self, origin):
        # Enable cross-domain request
        # logging.info(origin)
        return True
    
    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        self.uuid = str(uuid.uuid4())
        ChatSocketHandler.waiters[self.uuid] = self
        session_info = {
            'type': "CONNECT",
            'id': self.uuid,
        }

        waiter = self
        try:
            waiter.write_message(json.dumps(session_info))
        except:
            logging.error("Error sending message", exc_info=True)

    def on_close(self):
        ChatSocketHandler.waiters.pop(self.uuid)

    @staticmethod
    def on_caculate_success(uuid, index):
        logging.info("on_caculate_success")
        cacalation_notification_info = {
            'type': "NOTIFICATION_CACULATION_SUCCESS",
            'index': index
        }
        if uuid in ChatSocketHandler.waiters:
            waiter = ChatSocketHandler.waiters[uuid]
            waiter.write_message(json.dumps(cacalation_notification_info))


class PikaClient(object):
    def __init__(self):
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.connection = None
        self.channel = None


        self._delivery_tag = 0
        self.parameters = pika.ConnectionParameters(rabbitmq_server)

    def connect(self):
        self.connection = TornadoConnection(self.parameters, on_open_callback=self.on_connected, stop_ioloop_on_close=False, on_open_error_callback=self.on_open_error)
        self.connection.add_on_close_callback(self.on_closed)

    def on_open_error(self, unused_connection, err):
        sys.exit(1)

    def on_connected(self, connection):
        logging.info('PikaClient: connected to RabbitMQ')
        self.connection.channel(self.on_exchange_declare)

    def on_exchange_declare(self, channel):
        logging.info('PikaClient: Channel %s open, Declaring exchange' % channel)
        self.channel = channel
        self.channel.exchange_declare(self.on_queue_declare, exchange='notification', exchange_type='direct')

    def on_queue_declare(self, method_frame):
        logging.info('PikaClient: Channel open, Declaring queue')
        self.channel.queue_declare(self.on_queue_bind, queue='notification') #, durable=True)

    def on_queue_bind(self, method_frame):
        logging.info('Queue bound')
        self.channel.queue_bind(self.on_consume_bind, queue="notification", exchange="notification", routing_key="notification")

    def on_consume_bind(self, frame):
        logging.info("Consume bind")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_response, queue='notification', no_ack=False)

    def on_response(self, channel, method, properties, body):
        logging.info('on_response')
        message=pickle.loads(body)
        logging.info(message)
        ChatSocketHandler.on_caculate_success(message['id'], message['index'])
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