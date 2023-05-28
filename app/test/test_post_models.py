import unittest
import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.api.resources import Status
from app.api.store import ModelStore


class TestPostModels(unittest.TestCase):
    _test_client: TestClient = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._test_client = TestClient(app)

    def tearDown(self) -> None:
        # Reset the model store after each test
        self._test_client.app.state.model_store = ModelStore()

    def test_successful_post_models(self):
        model_config = {
            'config': {
                'data_source': 'https://myexampleapi.com',
                'data_api_key': 'my_example_api_key'
            }
        }
        response = self._test_client.post('/models', json=model_config)
        # Status code should be 201 for a good input
        self.assertEqual(response.status_code, 201)
        resp_json = response.json()
        self.assertIsNotNone(resp_json)
        # Check there is a location header
        self.assertIn('Location', response.headers)
        # And that the header has the correct value
        expected_url = f'{self._test_client.base_url}/models/{resp_json["id"]}'
        self.assertEqual(response.headers['Location'], expected_url)
        # There should only be two keys in the response body
        self.assertCountEqual(['id', 'status'], resp_json)
        # Check the ID is a valid UUID (will raise a ValueError if it's not)
        model_id = uuid.UUID(resp_json['id'])
        # The status should be one of the Enum types
        self.assertIn(resp_json['status'], [val.value for val in Status])
        # Check the model has been added to the in memory database
        self.assertIn(resp_json['id'], self._test_client.app.state.model_store)

    def test_post_models_with_bad_url(self) -> None:
        model_config = {
            'config': {
                'data_source': 'http://icnompleteurl',
                'data_api_key': 'my_example_api_key'
            }
        }
        response = self._test_client.post('/models', json=model_config)
        # This should return 400, but FastAPI validation rejects the input with a 422 error
        self.assertEqual(response.status_code, 422)

    def test_post_models_with_missing_key(self) -> None:
        model_config = {
            'config': {
                'data_api_key': 'my_example_api_key'
            }
        }
        response = self._test_client.post('/models', json=model_config)
        # This should return 400, but FastAPI validation rejects the input with a 422 error
        self.assertEqual(response.status_code, 422)
        model_config = {
            'config': {
                'data_source': 'https://myexampleapi.com',
            }
        }
        response = self._test_client.post('/models', json=model_config)
        # This should return 400, but FastAPI validation rejects the input with a 422 error
        self.assertEqual(response.status_code, 422)

    def test_post_models_with_inaccessible_url(self) -> None:
        # We should get a Bad Request error if the data source is inaccessible (contains airbus.com)
        model_config = {
            'config': {
                'data_source': 'https://airbus.com/some/data/source',
                'data_api_key': 'my_example_api_key'
            }
        }
        response = self._test_client.post('/models', json=model_config)
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
