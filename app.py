import time, celeryconfig
from flask import Flask, jsonify, request
from celery import Celery
from subprocess import Popen, PIPE
import jsonschema
from flask_jsonschema_validator import JSONSchemaValidator

celery = Celery()
celery.config_from_object(celeryconfig)


@celery.task(bind=True, queue='celery')
def add(self, x, y):
    cmd = [x, y]
    meta = {'cmd': x, 'arg': y}
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    self.update_state(state='RUNNING', meta={'cmd': cmd, 'arg': y})
    time.sleep(60)
    stdout, stderr = p.communicate()
    output = {'stderr': stderr, 'stdout': stdout}
    return (
     meta, output)


app = Flask(__name__)
JSONSchemaValidator(app=app, root='./')


@app.route('/longtask', methods=['POST'])
@app.validate('schema', 'register')
def long_task():
    data = request.get_json()
    x = data['argx']
    y = data['argy']
    task = add.delay(x, y).id
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
