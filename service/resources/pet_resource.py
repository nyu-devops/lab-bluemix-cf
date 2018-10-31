"""
This module contains all of Resources for the Pet Shop API
"""
from flask import abort, request
from flask_restful import Resource
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import BadRequest
from service import app, api
from service.models import Pet, DataValidationError

######################################################################
#  PATH: /pets/{id}
######################################################################
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
        pet.save()
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
