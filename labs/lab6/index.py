from flask import Flask
import socket


hostname = socket.gethostname()

app = Flask(__name__)

@app.route("/")
def hello():
    return 'Hello World from <b>[{}]</b>!'.format(hostname)

app.run(host='0.0.0.0', port=5000)
