# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Pet API Controller

This modules provides a REST API for the Pet Model

Paths:
------
GET /pets - Lists all of the Pets
GET /pets/{id} - Retrieves a single Pet with the specified id
POST /pets - Creates a new Pet
PUT /pets/{id} - Updates a single Pet with the specified id
DELETE /pets/{id} - Deletes a single Pet with the specified id
POST /pets/{id}/purchase - Action to purchase a Pet
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from models import Pet, DataValidationError

# Create Flask application
app = Flask(__name__)
app.config['LOGGING_LEVEL'] = logging.INFO

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(400)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), 400

@app.errorhandler(404)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=404, error='Not Found', message=message), 404

@app.errorhandler(405)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=405, error='Method not Allowed', message=message), 405

@app.errorhandler(415)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=415, error='Unsupported media type', message=message), 415

@app.errorhandler(500)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=500, error='Internal Server Error', message=message), 500


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Send back the home page """
    return app.send_static_file('index.html')

######################################################################
# LIST ALL PETS
######################################################################
@app.route('/pets', methods=['GET'])
def list_pets():
    """ Returns all of the Pets """
    pets = []
    category = request.args.get('category')
    name = request.args.get('name')
    available = request.args.get('available')
    if category:
        pets = Pet.find_by_category(category)
    elif name:
        pets = Pet.find_by_name(name)
    elif available:
        pets = Pet.find_by_availability(available)
    else:
        pets = Pet.all()

    results = [pet.serialize() for pet in pets]
    return make_response(jsonify(results), HTTP_200_OK)

######################################################################
# RETRIEVE A PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['GET'])
def get_pets(pet_id):
    """
    Retrieve a single Pet

    This endpoint will return a Pet based on it's id
    """
    pet = Pet.find(pet_id)
    if not pet:
        abort(HTTP_404_NOT_FOUND, "Pet with id '{}' was not found.".format(pet_id))
    return make_response(jsonify(pet.serialize()), HTTP_200_OK)

######################################################################
# ADD A NEW PET
######################################################################
@app.route('/pets', methods=['POST'])
def create_pets():
    """
    Creates a Pet

    This endpoint will create a Pet based the data in the body that is posted
    or data that is sent via an html form post.
    """
    data = {}
    # Check for form submission data
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        app.logger.info('Processing FORM data')
        data = {
            'name': request.form['name'],
            'category': request.form['category'],
            'available': request.form['available'].lower() in ['true', '1', 't']
        }
    else:
        app.logger.info('Processing JSON data')
        data = request.get_json()
    pet = Pet()
    pet.deserialize(data)
    pet.save()
    message = pet.serialize()
    return make_response(jsonify(message), HTTP_201_CREATED,
                         {'Location': url_for('get_pets', pet_id=pet.id, _external=True)})

######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['PUT'])
def update_pets(pet_id):
    """
    Update a Pet

    This endpoint will update a Pet based the body that is posted
    """
    pet = Pet.find(pet_id)
    if not pet:
        abort(HTTP_404_NOT_FOUND, "Pet with id '{}' was not found.".format(pet_id))
    pet.deserialize(request.get_json())
    pet.id = pet_id
    pet.save()
    return make_response(jsonify(pet.serialize()), HTTP_200_OK)


######################################################################
# DELETE A PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pets(pet_id):
    """
    Delete a Pet

    This endpoint will delete a Pet based the id specified in the path
    """
    pet = Pet.find(pet_id)
    if pet:
        pet.delete()
    return make_response('', HTTP_204_NO_CONTENT)

######################################################################
# PURCHASE A PET
######################################################################
@app.route('/pets/<int:pet_id>/purchase', methods=['PUT'])
def purchase_pets(pet_id):
    """ Purchase a Pet """
    pet = Pet.find(pet_id)
    if not pet:
        abort(HTTP_404_NOT_FOUND, "Pet with id '{}' was not found.".format(pet_id))
    if not pet.available:
        abort(HTTP_400_BAD_REQUEST, "Pet with id '{}' is not available.".format(pet_id))
    pet.available = False
    pet.save()
    return make_response(jsonify(pet.serialize()), HTTP_200_OK)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

@app.before_first_request
def init_db(redis=None):
    """ Initlaize the model """
    Pet.init_db(redis)

# load sample data
def data_load(payload):
    """ Loads a Pet into the database """
    pet = Pet(0, payload['name'], payload['category'])
    pet.save()

def data_reset():
    """ Removes all Pets from the database """
    Pet.remove_all()

# @app.before_first_request
def initialize_logging(log_level):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print "************************************************************"
    print "        P E T   R E S T   A P I   S E R V I C E "
    print "************************************************************"
    initialize_logging(app.config['LOGGING_LEVEL'])
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
