"""
This module contains routes without Resources
"""
from flask import abort
from flask_api import status
from flask_restful import Resource
from service.models import Pet

######################################################################
# PURCHASE A PET
######################################################################
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
        pet.save()
        return pet.serialize(), status.HTTP_200_OK
