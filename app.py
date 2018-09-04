import time, celeryconfig
from flask import Flask, jsonify, request, Response
from celery import Celery
from subprocess import Popen, PIPE
import jsonschema
from flask_jsonschema_validator import JSONSchemaValidator

celery = Celery()
celery.config_from_object(celeryconfig)


@celery.task(bind=True, queue='celery')
def add(self, x, y):
    cmd = [x, y]
    meta = {'argx': x, 'argy': y}
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    self.update_state(state='RUNNING', meta={'argx': cmd, 'argy': y})
    time.sleep(60)
    stdout, stderr = p.communicate()
    return (
     meta, stderr, stdout)


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
    info = add.AsyncResult(task).info
    state = add.AsyncResult(task).state
    return jsonify(state, info, task)


@app.errorhandler(jsonschema.ValidationError)
def onValidationError(e):
    return Response('There was a validation error: ' + str(e), 400)
