import time

from flask import Flask
from flask_redis import FlaskRedis

from config import Config


redis_store = FlaskRedis()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    redis_store.init_app(app)
    return app

def get_hit_count():
    retries = 5
    while True:
        try:
            return redis_store.incr('hits')
        except:
            if retries == 0:
                exit(1)
            retries -= 1
            time.sleep(0.5)

def init_route(app):
    @app.route('/')
    def index():
        count = get_hit_count()
        return 'Hello World! I have been seen {} times.\n'.format(count)

if __name__ == "__main__":
    app = create_app()
    init_route(app)
    app.run(host="0.0.0.0", port=5000, debug=True)
