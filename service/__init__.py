"""
Package: app

Package for the application models and services
This module also sets up the logging to be used with gunicorn
"""
import os
import sys
import logging
from flask import Flask
from flask_restx import Api
from .models import Pet, DataValidationError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'please, tell nobody... Shhhh'
app.config['LOGGING_LEVEL'] = logging.INFO

api = Api(app,
          version='1.0.0',
          title='Pet Demo REST API Service',
          description='This is a sample server Pet store server.',
          default='pets',
          default_label='Pet shop operations',
          doc='/apidocs/',
          prefix='/api'
         )

from service.resources import (
    PetResource,
    PetCollection,
    PurchaseAction
)

# Set up logging for production
app.logger.propagate = False
print('Setting up logging for {}...'.format(__name__))
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

app.logger.info(70 * '*')
app.logger.info('  P E T   S E R V I C E   R U N N I N G  '.center(70, '*'))
app.logger.info(70 * '*')
app.logger.info('Logging established')


@app.before_first_request
def init_db(dbname="pets"):
    """ Initlaize the model """
    Pet.init_db(dbname)
