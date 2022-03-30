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
Pet Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color

nosetests --stop tests/test_pets.py:TestPets
"""
import os
import json
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from requests import HTTPError, ConnectionError
from service.models import Pet, Gender, DataValidationError
from service import init_db
from tests.factories import PetFactory

# This is for production testing
# Comment this out when debugging
logging.disable(logging.CRITICAL)

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPets(TestCase):
    """Test Cases for Pet Model"""

    def setUp(self):
        """Initialize the Cloudant database"""
        init_db("tests")
        Pet.remove_all()

    def _create_pets(self, count: int) -> list:
        """Creates a collection of pets in the database"""
        pet_collection = []
        for _ in range(count):
            pet = PetFactory()
            pet.create()
            pet_collection.append(pet)
        return pet_collection        

    def test_create_a_pet(self):
        """Create a pet and assert that has correct attributes"""
        pet = Pet(name="Fido", category="dog", available=True, gender=Gender.MALE)
        self.assertTrue(pet is not None)
        self.assertEqual(pet.id, None)
        self.assertEqual(pet.name, "Fido")
        self.assertEqual(pet.category, "dog")
        self.assertEqual(pet.available, True)
        self.assertEqual(pet.gender, Gender.MALE)
        pet = Pet(name="Fido", category="dog", available=False, gender=Gender.FEMALE)
        self.assertEqual(pet.available, False)
        self.assertEqual(pet.gender, Gender.FEMALE)

    def test_add_a_pet(self):
        """Create a pet and add it to the database"""
        pets = Pet.all()
        self.assertEqual(pets, [])
        pet = PetFactory()
        logging.debug("Pet: %s", pet.serialize())
        self.assertNotEqual(pet, None)
        self.assertEqual(pet.id, None)
        pet.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertNotEqual(pet.id, None)
        pets = Pet.all()
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].name, pet.name)
        self.assertEqual(pets[0].category, pet.category)
        self.assertEqual(pets[0].available, pet.available)
        self.assertEqual(pets[0].gender, pet.gender)

    def test_create_a_pet_with_no_name(self):
        """Create a Pet with no name"""
        pet = Pet(None, "cat")
        self.assertRaises(DataValidationError, pet.create)

    def test_read_a_pet(self):
        """Read a Pet"""
        pet = PetFactory()
        logging.debug(pet)
        pet.create()
        self.assertIsNotNone(pet.id)
        # Fetch it back
        found_pet = Pet.find(pet.id)
        self.assertEqual(found_pet.id, pet.id)
        self.assertEqual(found_pet.name, pet.name)
        self.assertEqual(found_pet.category, pet.category)
        self.assertEqual(found_pet.gender, pet.gender)

    def test_update_a_pet(self):
        """Update a Pet"""
        pet = PetFactory()
        logging.debug(pet)
        pet.create()
        logging.debug(pet)
        self.assertIsNotNone(pet.id)
        # Change it an save it
        pet.category = "k9"
        original_id = pet.id
        pet.update()
        self.assertEqual(pet.id, original_id)
        self.assertEqual(pet.category, "k9")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        pets = Pet.all()
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].id, pet.id)
        self.assertEqual(pets[0].category, "k9")

    def test_delete_a_pet(self):
        """Delete a Pet"""
        pet = PetFactory()
        pet.create()
        self.assertEqual(len(Pet.all()), 1)
        # delete the pet and make sure it isn't in the database
        pet.delete()
        self.assertEqual(len(Pet.all()), 0)

    def test_list_all_pets(self):
        """List Pets in the database"""
        pets = Pet.all()
        self.assertEqual(pets, [])
        # Create 5 Pets
        for i in range(5):
            pet = PetFactory()
            pet.create()
        # See if we get back 5 pets
        pets = Pet.all()
        self.assertEqual(len(pets), 5)

    def test_serialize_a_pet(self):
        """Test serialization of a Pet"""
        pet = PetFactory()
        data = pet.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("name", data)
        self.assertEqual(data["name"], pet.name)
        self.assertIn("category", data)
        self.assertEqual(data["category"], pet.category)
        self.assertIn("available", data)
        self.assertEqual(data["available"], pet.available)
        self.assertIn("gender", data)
        self.assertEqual(data["gender"], pet.gender.name)

    def test_deserialize_a_pet(self):
        """Test deserialization of a Pet"""
        data = {
            "name": "Kitty",
            "category": "cat",
            "available": True,
            "gender": "FEMALE",
        }
        pet = Pet()
        pet.deserialize(data)
        self.assertNotEqual(pet, None)
        self.assertEqual(pet.id, None)
        self.assertEqual(pet.name, "Kitty")
        self.assertEqual(pet.category, "cat")
        self.assertEqual(pet.available, True)
        self.assertEqual(pet.gender, Gender.FEMALE)

    def test_deserialize_missing_data(self):
        """Test deserialization of a Pet with missing data"""
        data = {"name": "Kitty", "category": "cat"}
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_with_no_data(self):
        """Deserialize a Pet that has no data"""
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, None)

    def test_deserialize_with_no_name(self):
        """Deserialize a Pet that has no name"""
        data = {"category": "cat"}
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_with_no_gender(self):
        """Deserialize a Pet with no gender data"""
        data = {"name": "fido", "category": "dog", "available": True}
        pet = Pet()
        pet.deserialize(data)
        self.assertEqual(pet.gender, Gender.UNKNOWN)

    def test_deserialize_with_bad_gender(self):
        """Deserialize a Pet with bad gender data"""
        data = {"name": "fido", "category": "dog", "available": True, "gender": "foo"}
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        data = "this is not a dictionary"
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_bad_available(self):
        """Test deserialization of bad available attribute"""
        test_pet = PetFactory()
        data = test_pet.serialize()
        data["available"] = "true"
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_lower_case_gender(self):
        """Test deserialization with lower case gender"""
        test_pet = PetFactory()
        data = test_pet.serialize()
        data["gender"] = "male"  # lower case
        pet = Pet()
        pet.deserialize(data)
        self.assertEqual(pet.gender, Gender.MALE)

    def test_find_pet(self):
        """Find a Pet by id"""
        pets = self._create_pets(5)
        saved_pet = pets[0]
        pet = Pet.find(saved_pet.id)
        self.assertIsNot(pet, None)
        self.assertEqual(pet.id, saved_pet.id)
        self.assertEqual(pet.name, saved_pet.name)
        self.assertEqual(pet.category, saved_pet.category)
        self.assertEqual(pet.available, saved_pet.available)
        self.assertEqual(pet.gender, saved_pet.gender)
        
    def test_pet_not_found(self):
        """Pet not found"""
        pet = Pet.find("foo")
        self.assertIsNone(pet)

    def test_find_by_name(self):
        """Find a Pet by Name"""
        self._create_pets(5)
        saved_pet = PetFactory()
        saved_pet.name = "Rumpelstiltskin"
        saved_pet.create()
        # search by name
        pets = Pet.find_by_name("Rumpelstiltskin")
        self.assertNotEqual(len(pets), 0)
        pet = pets[0]
        self.assertEqual(pet.name, "Rumpelstiltskin")
        self.assertEqual(pet.category, saved_pet.category)
        self.assertEqual(pet.available, saved_pet.available)
        self.assertEqual(pet.gender, saved_pet.gender)

    def test_find_by_category(self):
        """Find a Pet by Category"""
        pets = self._create_pets(5)
        category = pets[0].category
        category_count =  len([pet for pet in pets if pet.category == category])
        logging.debug("Looking for %d Pets in category %s", category_count, category)
        found_pets = Pet.find_by_category(category)
        self.assertEqual(len(found_pets), category_count)
        for pet in found_pets:
            self.assertEqual(pet.category, category)

    def test_find_by_availability(self):
        """Find a Pet by Availability"""
        pets = self._create_pets(5)
        available = pets[0].available
        available_count = len([pet for pet in pets if pet.available == available])
        logging.debug("Looking for %d Pets where availabe is %s", available_count, available)
        found_pets = Pet.find_by_availability(available)
        self.assertEqual(len(found_pets), available_count)
        for pet in found_pets:
            self.assertEqual(pet.available, available)

    def test_find_by_gender(self):
        """Find a Pet by Gender"""
        pets = self._create_pets(5)
        gender = pets[0].gender
        gender_count =  len([pet for pet in pets if pet.gender == gender])
        logging.debug("Looking for %d Pets where gender is %s", gender_count, gender)
        found_pets = Pet.find_by_gender(gender.name)
        self.assertEqual(len(found_pets), gender_count)
        for pet in found_pets:
            self.assertEqual(pet.gender, gender)

    def test_create_query_index(self):
        """Test create query index"""
        Pet("fido", "dog", False).create()
        Pet("kitty", "cat", True).create()
        Pet.create_query_index("category")

    ######################################################################
    #  P A T C H   A N D   M O C K   T E S T   C A S E S
    ######################################################################

    def test_disconnect(self):
        """Test Disconnet"""
        Pet.disconnect()
        pet = Pet("fido", "dog", False)
        self.assertRaises(AttributeError, pet.create)

    def test_connect(self):
        """Test Connect"""
        Pet.disconnect()
        Pet.connect()
        pet = Pet("fido", "dog", False)
        pet.create()

    @patch("cloudant.database.CloudantDatabase.create_document")
    def test_http_error(self, bad_mock):
        """Test a Bad Create with HTTP error"""
        bad_mock.side_effect = HTTPError()
        pet = Pet("fido", "dog", False)
        pet.create()
        self.assertIsNone(pet.id)

    @patch("cloudant.document.Document.exists")
    def test_document_not_exist(self, bad_mock):
        """Test a Bad Document Exists"""
        bad_mock.return_value = False
        pet = Pet("fido", "dog", False)
        pet.create()
        self.assertIsNone(pet.id)

    @patch("cloudant.database.CloudantDatabase.__getitem__")
    def test_key_error_on_update(self, bad_mock):
        """Test KeyError on update"""
        bad_mock.side_effect = KeyError()
        pet = Pet("fido", "dog", False)
        pet.create()
        pet.name = "Fifi"
        pet.update()
        # self.assertEqual(pet.name, 'fido')

    @patch("cloudant.database.CloudantDatabase.__getitem__")
    def test_key_error_on_delete(self, bad_mock):
        """Test KeyError on delete"""
        bad_mock.side_effect = KeyError()
        pet = Pet("fido", "dog", False)
        pet.create()
        pet.delete()

    @patch("cloudant.client.Cloudant.__init__")
    def test_connection_error(self, bad_mock):
        """Test Connection error handler"""
        bad_mock.side_effect = ConnectionError()
        self.assertRaises(AssertionError, Pet.init_db, "test")


# These last two test will fail in the cloud because we are not
# in control of the database name. They are left here as examples
# of how to patch environment variables in general.

# @patch.dict(os.environ, {"VCAP_SERVICES": json.dumps(VCAP_SERVICES)})
# def test_vcap_services(self):
#     """Test if VCAP_SERVICES works"""
#     Pet.init_db("tests")
#     self.assertIsNotNone(Pet.client)
#     Pet("fido", "dog", True).create()
#     pets = Pet.find_by_name("fido")
#     self.assertNotEqual(len(pets), 0)
#     self.assertEqual(pets[0].name, "fido")
