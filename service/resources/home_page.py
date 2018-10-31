"""
This module contains routes without Resources
"""
from flask_restful import Resource
from service import app

######################################################################
# GET /
######################################################################
class HomePage(Resource):
    """ Resource fior the Home Page """
    def get(self):
        """ Returns the index page """
        return app.send_static_file('index.html')

# @app.route('/')
# def index():
#     """ Send back the home page """
#     return app.send_static_file('index.html')
