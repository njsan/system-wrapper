## Broker settings.
broker_url = 'redis://192.168.99.100:32770'

# List of modules to import when the Celery worker starts.
imports = ('celery.task',)

## Using the database to store task state and results.
result_backend = 'redis://192.168.99.100:32770'

task_annotations = {'tasks.add': {'rate_limit': '10/s'}}
