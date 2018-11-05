import time
import os
import msgpackrpc
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    client = msgpackrpc.Client(msgpackrpc.Address("localhost", 18900))
    result = client.call('get_result', time.time())
    return '{}'.format(result)

if __name__ == '__main__':
    app.run(host='172.17.51.1', port=7788)
