######################################################################
# Copyright 2016, 2022 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Pet API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestPetServer
"""

import os
import logging

from unittest.mock import MagicMock, patch
from unittest import TestCase
from urllib.parse import quote_plus
from service import app, status
from service.models import Pet
from .factories import PetFactory

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
logging.disable(logging.CRITICAL)

BASE_URL = "/pets"
CONTENT_TYPE_JSON = "application/json"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestPetServer(TestCase):
    """Pet Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False

    def setUp(self):
        self.app = app.test_client()
        Pet.init_db("tests")
        Pet.remove_all()

    def tearDown(self):
        Pet.remove_all()

    ######################################################################
    # U T I L I T Y   F U N C T I O N S
    ######################################################################

    def _create_pets(self, count):
        """Factory method to create pets in bulk"""
        pets = []
        for _ in range(count):
            test_pet = PetFactory()
            logging.info(f"PetFactory: {test_pet.serialize()}")
            resp = self.app.post(
                BASE_URL, json=test_pet.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test pet"
            )
            new_pet = resp.get_json()
            logging.info(f"JSON Returned: {new_pet}")
            test_pet.id = new_pet["_id"]
            pets.append(test_pet)
        return pets

    ######################################################################
    # T E S T   C R U D  E N D P O I N T S
    ######################################################################

    def test_index(self):
        """Test the Home Page"""
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"Pet Demo REST API Service", resp.data)

    def test_get_pet_list(self):
        """Get a list of Pets"""
        self._create_pets(5)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_pet(self):
        """Get a single Pet"""
        # get the id of a pet
        test_pet = self._create_pets(1)[0]
        resp = self.app.get(f"/pets/{test_pet.id}", content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_pet.name)

    def test_get_pet_not_found(self):
        """Get a Pet thats not found"""
        resp = self.app.get("/pets/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_pet(self):
        """Create a new Pet"""
        test_pet = PetFactory()
        logging.debug(test_pet)
        resp = self.app.post(
            BASE_URL, json=test_pet.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_pet = resp.get_json()
        self.assertEqual(new_pet["name"], test_pet.name, "Names do not match")
        self.assertEqual(
            new_pet["category"], test_pet.category, "Categories do not match"
        )
        self.assertEqual(
            new_pet["available"], test_pet.available, "Availability does not match"
        )
        self.assertEqual(
            new_pet["gender"], test_pet.gender.name, "Gender does not match"
        )
        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_pet = resp.get_json()
        self.assertEqual(new_pet["name"], test_pet.name, "Names do not match")
        self.assertEqual(
            new_pet["category"], test_pet.category, "Categories do not match"
        )
        self.assertEqual(
            new_pet["available"], test_pet.available, "Availability does not match"
        )
        self.assertEqual(
            new_pet["gender"], test_pet.gender.name, "Gender does not match"
        )

    def test_create_pet_no_data(self):
        """Create a Pet with missing data"""
        resp = self.app.post(BASE_URL, json={}, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pet_no_content_type(self):
        """Create a Pet with no content type"""
        resp = self.app.post(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pet(self):
        """Update an existing Pet"""
        # create a pet to update
        test_pet = PetFactory()
        resp = self.app.post(
            BASE_URL, json=test_pet.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_pet = resp.get_json()
        logging.debug(new_pet)
        new_pet["category"] = "unknown"
        resp = self.app.put(
            f"/pets/{new_pet.get('_id')}",
            json=new_pet,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_pet = resp.get_json()
        self.assertEqual(updated_pet["category"], "unknown")

    def test_update_pet_not_found(self):
        """Update a Pet that doesn't exist"""
        resp = self.app.put(
            "/pets/foo",
            json={},
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_pet_bad_content_type(self):
        """Update a Pet using the wrong content type"""
        resp = self.app.put(
            "/pets/foo",
            json={},
            content_type="text/html",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_delete_pet(self):
        """Delete a Pet"""
        test_pet = self._create_pets(1)[0]
        resp = self.app.delete(
            f"{BASE_URL}/{test_pet.id}", content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get("{BASE_URL}/{test_pet.id}", content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    # T E S T   A C T I O N S
    ######################################################################

    def test_purchase_a_pet(self):
        """ Purchase a Pet """
        pet = PetFactory()
        pet.available = True
        resp = self.app.post(
            BASE_URL, json=pet.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pet_data = resp.get_json()
        pet_id = pet_data["_id"]
        logging.info(f"Created Pet with id {pet_id} = {pet_data}")

        # Request to purchase a Pet
        resp = self.app.put(f'{BASE_URL}/{pet_id}/purchase')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Retrieve the Pet and make sue it is no longer available
        resp = self.app.get(f'{BASE_URL}/{pet_id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        pet_data = resp.get_json()
        self.assertEqual(pet_data['_id'], pet_id)
        self.assertEqual(pet_data['available'], False)

    def test_purchase_not_available(self):
        """ Purchase a Pet that is not available """
        pet = PetFactory()
        pet.available = False
        resp = self.app.post(
            BASE_URL, json=pet.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pet_data = resp.get_json()
        pet_id = pet_data["_id"]
        logging.info(f"Created Pet with id {pet_id} = {pet_data}")

        # Request to purchase a Pet should fail
        resp = self.app.put(f'{BASE_URL}/{pet_id}/purchase')
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_purchase_a_pet_not_found(self):
        """ Purchase a Pet not found """
        resp = self.app.put(f'{BASE_URL}/foo/purchase')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    # T E S T   Q U E R Y   S T R I N G S
    ######################################################################

    def test_query_pets_by_name(self):
        """Query Pets by Name"""
        pets = self._create_pets(10)
        test_name = pets[0].name
        name_list = [pet for pet in pets if pet.name == test_name]
        logging.info(f"Name={test_name}: {len(name_list)} = {name_list}")
        resp = self.app.get(BASE_URL, query_string=f"name={quote_plus(test_name)}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(name_list))
        # check the data just to be sure
        for pet in data:
            self.assertEqual(pet["name"], test_name)

    def test_query_pets_by_category(self):
        """Query Pets by Category"""
        pets = self._create_pets(10)
        test_category = pets[0].category
        category_list = [pet for pet in pets if pet.category == test_category]
        logging.info(
            f"Category={test_category}: {len(category_list)} = {category_list}"
        )
        resp = self.app.get(
            BASE_URL, query_string=f"category={quote_plus(test_category)}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(category_list))
        # check the data just to be sure
        for pet in data:
            self.assertEqual(pet["category"], test_category)

    def test_query_pets_by_availability(self):
        """Query Pets by Availability"""
        pets = self._create_pets(10)
        test_available = pets[0].available
        available_list = [pet for pet in pets if pet.available == test_available]
        logging.info(
            f"Available={test_available}: {len(available_list)} = {available_list}"
        )
        resp = self.app.get(BASE_URL, query_string=f"available={str(test_available)}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(available_list))
        # check the data just to be sure
        for pet in data:
            self.assertEqual(pet["available"], test_available)

    def test_query_pets_by_gender(self):
        """Query Pets by Gender"""
        pets = self._create_pets(10)
        test_gender = pets[0].gender.name
        gender_list = [pet for pet in pets if pet.gender.name == test_gender]
        logging.info(f"Gender={test_gender}: {len(gender_list)} = {gender_list}")
        resp = self.app.get(BASE_URL, query_string=f"gender={quote_plus(test_gender)}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(gender_list))
        # check the data just to be sure
        for pet in data:
            self.assertEqual(pet["gender"], test_gender)

    ######################################################################
    # T E S T   E R R O R   H A N D L E R S
    ######################################################################

    def test_method_not_allowed(self):
        """ Test Method Not Allowed """
        # There is no endpoint for PUT on the base url
        resp = self.app.put(f'{BASE_URL}')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch('service.routes.Pet.find_by_name')
    def test_server_error(self, server_error_mock):
        """ Test a 500 Internal Server Error Handler """
        server_error_mock.return_value = None # code expects a list
        # Turn off testing to allow production behavior
        app.config["TESTING"] = False
        resp = self.app.get(BASE_URL, query_string='name=fido')
        app.config["TESTING"] = True
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
