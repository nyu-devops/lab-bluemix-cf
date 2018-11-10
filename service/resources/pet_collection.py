"""
This module contains the Pet Collection Resource
"""
from flask import request, abort
from flask_restful import Resource
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import BadRequest
from service import app, api
from service.models import Pet, DataValidationError
from . import PetResource

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
            pets = Pet.find_by_availability(available)
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
            data = {
                'name': request.form['name'],
                'category': request.form['category'],
                'available': request.form['available'].lower() in ['true', '1', 't']
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
        pet.save()
        app.logger.info('Pet with new id [%s] saved!', pet.id)
        location_url = api.url_for(PetResource, pet_id=pet.id, _external=True)
        return pet.serialize(), status.HTTP_201_CREATED, {'Location': location_url}
