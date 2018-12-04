import time
import os
import pickle
import json
import logging

from flask import Flask, request
from flask_cors import CORS
from flask_redis import FlaskRedis

import pika

from config import Config

logging.level = logging.DEBUG

redis_hashmap_key = os.environ.get("REDIS_HASHMAP_KEY")
rabbitmq_server = os.environ.get("RABBITMQ_SERVER")

redis_store = FlaskRedis()
pika_connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_server))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/*": {"origins": "*"}})

    redis_store.init_app(app)

    return app


def init_route(app):
    @app.route('/')
    def index():
        # health check
        return 'ok'

    @app.route('/fibonacci/<int:index>',  methods=['post', 'get'])
    def getFibonacci(index):
        cache_value = redis_store.hget(redis_hashmap_key, index)
        # cache_value = None 
        if cache_value is not None:
            return get_result_cached(index, int(cache_value))
        
        session_uuid = request.headers.get('session_uuid')
        app.logger.info(session_uuid)
        add_calc_task(session_uuid, index)
        
        return get_result_miss()


def get_result_cached(index, value):
    return json.dumps({
        'type': 'CACHED',
        'index': index,
        'value': value,
    })


def get_result_miss():
    return json.dumps({
        'type': 'MISS',
    })


def add_calc_task(session_uuid, index):
    global pika_connection
    message = {
        'uuid': session_uuid,
        'index': index,
    }
    #calc_fibonacci
    try:
        channel = pika_connection.channel()
        channel.exchange_declare(exchange='calc_fibonacci', exchange_type='direct')
        channel.queue_declare(queue='calc_fibonacci')
    
        channel.basic_publish(exchange='calc_fibonacci', routing_key='calc_fibonacci', body=pickle.dumps(message))
    except pika.exceptions.ConnectionClosed:
        app.logger.info('reconnect')
        pika_connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_server))
        channel = pika_connection.channel()
        channel.exchange_declare(exchange='calc_fibonacci', exchange_type='direct')
        channel.basic_publish(exchange='calc_fibonacci', routing_key='calc_fibonacci', body=pickle.dumps(message))
    app.logger.info('add_calc_task')


if __name__ == "__main__":
    app = create_app()
    init_route(app)
    app.run(host="0.0.0.0", port=5000, debug=True)
