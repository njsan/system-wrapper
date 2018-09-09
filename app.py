import time
import celeryconfig
import jsonschema
from flask import Flask, jsonify, request
from celery import Celery
from subprocess import Popen, PIPE
from flask_jsonschema_validator import JSONSchemaValidator
from helper import redis_extid_register, redis_extid_exist, redis_get_guid


celery = Celery()
celery.config_from_object(celeryconfig)


@celery.task(bind=True, queue='celery')
def add(self, x, y, z, q):
    cmd = [x, y, z]
    meta = {'cmd': x, 'argy': y, 'argz': z, 'extid': q}
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    self.update_state(state='RUNNING', meta={'cmd': cmd, 'argy': y, 'argz': z, 'extid': q})
    time.sleep(5)
    stdout, stderr = p.communicate()
    output = {'stderr': stderr, 'stdout': stdout}
    return (meta, output)


app = Flask(__name__)
JSONSchemaValidator(app=app, root='./')


@app.route('/longtask', methods=['POST'])
@app.validate('schema', 'register')
def long_task():
    ext_id = request.headers.get('X-Header-id')
    data = request.get_json()
    retval = redis_extid_exist(ext_id)
    if retval:
        guid = redis_get_guid(ext_id)
        state = {'conflict': {'ext_id': ext_id, 'guid': guid}}
        return jsonify(state), 409
    x = data['argx']
    y = data['argy']
    z = data['argz']
    task = add.delay(x, y, z, ext_id).id
    redis_extid_register(ext_id, task)
    return jsonify(task)


@app.route('/status/<task_id>')
def task_status(task_id):
    task = task_id
    state = {'id': task, 'state': add.AsyncResult(task).state, 'info': add.AsyncResult(task).info}
    return jsonify(state)


@app.errorhandler(jsonschema.ValidationError)
def onValidationError(e):
    error = str(e)
    return jsonify('There was a validation error: ' + error), 400
