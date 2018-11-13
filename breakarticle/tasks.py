from .factory import create_celery_app
import json
import logging
"""
from celery import Celery
broker = 'redis://redis:6379/0'
app = Celery('tasks', broker=broker)
"""
celery = create_celery_app()


# @celery.task()
@celery.task()
def test_delay(dpi_json):
    logging.info('Alan_test: test_delay: {}'.format(dpi_json))


@celery.task(ignore_result=True)
def test_queue(dpi_json):
    logging.info('Alan_test: test_queue: {}'.format(dpi_json))
