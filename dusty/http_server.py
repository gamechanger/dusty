from uuid import uuid1
from datetime import datetime
from collections import namedtuple
import calendar
import logging

from flask import Flask, request, jsonify

from .compiler.spec_assembler import get_assembled_specs
from .systems.docker import get_dusty_containers, get_docker_client

logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)

_consumers = {}

Consumer = namedtuple('Consumer', ['container_id', 'offset'])

def _app_name_from_forwarding_info(hostname, port):
    specs = get_assembled_specs()
    for app in specs['apps'].itervalues():
        for rule in app.get('host_forwarding', []):
            if rule['host_name'] == hostname and rule['host_port'] == int(port):
                return app.name
    raise ValueError('Could not find app for {}:{}'.format(hostname, port))

@app.route('/register-consumer', methods=['POST'])
def register_consumer():
    """Given a hostname and port attempting to be accessed,
    return a unique consumer ID for accessing logs from
    the referenced container."""
    global _consumers
    hostname, port = request.form['hostname'], request.form['port']

    app_name = _app_name_from_forwarding_info(hostname, port)
    containers = get_dusty_containers([app_name], include_exited=True)
    if not containers:
        raise ValueError('No container exists for app {}'.format(app_name))
    container = containers[0]

    new_id = uuid1()
    new_consumer = Consumer(container['Id'], datetime.utcnow())
    _consumers[str(new_id)] = new_consumer

    response = jsonify({'app_name': app_name, 'consumer_id': new_id})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    return response

@app.route('/consume/<consumer_id>', methods=['GET'])
def consume(consumer_id):
    """Given an existing consumer ID, return any new lines from the
    log since the last time the consumer was consumed."""
    global _consumers
    consumer = _consumers[consumer_id]

    client = get_docker_client()
    try:
        status = client.inspect_container(consumer.container_id)['State']['Status']
    except Exception as e:
        status = 'unknown'
    new_logs = client.logs(consumer.container_id,
                           stdout=True,
                           stderr=True,
                           stream=False,
                           timestamps=False,
                           since=calendar.timegm(consumer.offset.timetuple()))

    updated_consumer = Consumer(consumer.container_id, datetime.utcnow())
    _consumers[str(consumer_id)] = updated_consumer

    response = jsonify({'logs': new_logs, 'status': status})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    return response
