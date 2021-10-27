"""
RESTful Reseources for our Service
"""
from flask import request, abort
from flask_restx import Api, Resource
from werkzeug.exceptions import BadRequest
from service import app, api, status    # HTTP Status Codes
from service.models import Pet, DataValidationError

######################################################################
# GET /
######################################################################
@app.route('/')
def index():
    return app.send_static_file('index.html')


######################################################################
#  PATH: /pets/{id}
######################################################################
@api.route('/pets/<pet_id>')
class PetResource(Resource):
    """
    PetResource class

    Allows the manipulation of a single Pet
    GET /pet{id} - Returns a Pet with the id
    PUT /pet{id} - Update a Pet with the id
    DELETE /pet{id} -  Deletes a Pet with the id
    """

    def get(self, pet_id):
        """
        Retrieve a single Pet

        This endpoint will return a Pet based on it's id
        """
        app.logger.info("Request to Retrieve a pet with id [%s]", pet_id)
        pet = Pet.find(pet_id)
        if not pet:
            abort(status.HTTP_404_NOT_FOUND, "Pet with id '{}' was not found.".format(pet_id))
        return pet.serialize(), status.HTTP_200_OK


    def put(self, pet_id):
        """
        Update a Pet

        This endpoint will update a Pet based the body that is posted
        """
        app.logger.info('Request to Update a pet with id [%s]', pet_id)
        #check_content_type('application/json')
        pet = Pet.find(pet_id)
        if not pet:
            abort(status.HTTP_404_NOT_FOUND, "Pet with id '{}' was not found.".format(pet_id))

        payload = request.get_json()
        try:
            pet.deserialize(payload)
        except DataValidationError as error:
            raise BadRequest(str(error))

        pet.id = pet_id
        pet.update()
        return pet.serialize(), status.HTTP_200_OK

    def delete(self, pet_id):
        """
        Delete a Pet

        This endpoint will delete a Pet based the id specified in the path
        """
        app.logger.info('Request to Delete a pet with id [%s]', pet_id)
        pet = Pet.find(pet_id)
        if pet:
            pet.delete()
        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /pets
######################################################################
@api.route('/pets', strict_slashes=False)
class PetCollection(Resource):
    """ Handles all interactions with collections of Pets """

    def get(self):
        """ Returns all of the Pets """
        app.logger.info('Request to list Pets...')
        pets = []
        category = request.args.get('category')
        name = request.args.get('name')
        available = request.args.get('available')
        if category:
            app.logger.info('Filtering by category: %s', category)
            pets = Pet.find_by_category(category)
        elif name:
            app.logger.info('Filtering by name:%s', name)
            pets = Pet.find_by_name(name)
        elif available:
            app.logger.info('Filtering by available: %s', available)
            is_available = available.lower() in ['yes', 'y', 'true', 't', '1']
            pets = Pet.find_by_availability(is_available)
        else:
            pets = Pet.all()

        app.logger.info('[%s] Pets returned', len(pets))
        results = [pet.serialize() for pet in pets]
        return results, status.HTTP_200_OK

    def post(self):
        """
        Creates a Pet

        This endpoint will create a Pet based the data in the body that is posted
        or data that is sent via an html form post.
        """
        app.logger.info('Request to Create a Pet')
        content_type = request.headers.get('Content-Type')
        if not content_type:
            abort(status.HTTP_400_BAD_REQUEST, "No Content-Type set")

        data = {}
        # Check for form submission data
        if content_type == 'application/x-www-form-urlencoded':
            app.logger.info('Processing FORM data')
            app.logger.info(type(request.form))
            app.logger.info(request.form)
            data = {
                'name': request.form['name'],
                'category': request.form['category'],
                'available': request.form['available'].lower() in ['yes', 'y', 'true', 't', '1']
            }
        elif content_type == 'application/json':
            app.logger.info('Processing JSON data')
            data = request.get_json()
        else:
            message = 'Unsupported Content-Type: {}'.format(content_type)
            app.logger.info(message)
            abort(status.HTTP_400_BAD_REQUEST, message)

        pet = Pet()
        try:
            pet.deserialize(data)
        except DataValidationError as error:
            raise BadRequest(str(error))
        pet.create()
        app.logger.info('Pet with new id [%s] saved!', pet.id)
        location_url = api.url_for(PetResource, pet_id=pet.id, _external=True)
        return pet.serialize(), status.HTTP_201_CREATED, {'Location': location_url}


######################################################################
# PURCHASE A PET
######################################################################
@api.route('/pets/<pet_id>/purchase')
class PurchaseAction(Resource):
    """ Resource to Purchase a Pet """
    def put(self, pet_id):
        """ Purchase a Pet """
        pet = Pet.find(pet_id)
        if not pet:
            abort(status.HTTP_404_NOT_FOUND, "Pet with id '{}' was not found.".format(pet_id))
        if not pet.available:
            abort(status.HTTP_400_BAD_REQUEST, "Pet with id '{}' is not available.".format(pet_id))
        pet.available = False
        pet.update()
        return pet.serialize(), status.HTTP_200_OK
