from flask import Flask
from . import config
import os
import wtforms_json
from .model import db
from celery import Celery
import wtforms_json
import base64
import redis
import boto3

wtforms_json.init()


import simplejson

wtforms_json.init()

def create_app(config_obj=None):
    app = Flask(__name__)
    # load default settings
    app.config.from_object(config)
    # load environment-specific settings
    if os.getenv('BREAKTIME_ARTICLE_SETTINGS_PATH'):
        app.config.from_envvar('BREAKTIME_ARTICLE_SETTINGS_PATH')
    # load extra settings for testing purpose
    if config_obj:
        app.config.from_object(config_obj)

    with app.app_context():
        db.init_app(app)

        from breakarticle.api.hips import bp as hips_bp
        app.register_blueprint(hips_bp, url_prefix='/v0')

        aws_credential = {}
        if app.config['AWS_ACCESS_KEY_ID'] and len(app.config['AWS_ACCESS_KEY_ID']) > 0:
            aws_credential['aws_access_key_id'] = app.config['AWS_ACCESS_KEY_ID']
            aws_credential['aws_secret_access_key'] = app.config['AWS_ACCESS_SECRET']
        app.s3client = boto3.client('s3', **aws_credential)
    
        from breakarticle.api.patterns import bp as patterns_bp
        from breakarticle.api.devices import bp as devices_bp
        app.register_blueprint(patterns_bp, url_prefix='/v0')
        app.register_blueprint(devices_bp, url_prefix='/v0')

    return app


def create_celery_app(app=None):
    app = app or create_app()
    if app.config['CELERY_DISABLED']:
        return Celery(__name__)

    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    celery.app = app

    return celery

