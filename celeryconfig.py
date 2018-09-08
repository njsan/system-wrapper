## Broker settings.
broker_url = 'redis://192.168.99.100:32768'

# List of modules to import when the Celery worker starts.
imports = ('celery.task',)

## Using the database to store task state and results.
result_backend = 'redis://192.168.99.100:32768'

task_track_started = 'True'

#task_annotations = {'task.add': {'rate_limit': '10/s'}}
