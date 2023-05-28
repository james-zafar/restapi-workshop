import re
import unittest
import uuid
import random

from fastapi.testclient import TestClient

from app.main import app
from app.api.resources import Model
from app.api.store import ModelStore


class TestPostModels(unittest.TestCase):
    _test_client: TestClient = None

    @classmethod
    def setUpClass(cls) -> None:
        random.seed(500)
        cls._test_client = TestClient(app)

    def tearDown(self) -> None:
        # Reset the model store after each test
        self._test_client.app.state.model_store = ModelStore()

    def test_get_model(self) -> None:
        model = Model.new_model()
        self._test_client.app.state.model_store[str(model.id)] = model
        response = self._test_client.get(f'/models/{str(model.id)}')
        self.assertEqual(response.status_code, 200)
        expected_resp_body = {
            'id': str(model.id),
            'status': model.status.value
        }
        self.assertEqual(response.json(), expected_resp_body)

    def test_get_model_fails_with_fake_model(self) -> None:
        random_uuid = uuid.uuid4()
        self.assertNotIn(random_uuid, self._test_client.app.state.model_store)
        response = self._test_client.get(f'/models/{random_uuid}')
        self.assertEqual(response.status_code, 404)
        resp_json = response.json()
        # There should be an "errors" field
        self.assertIn('errors', resp_json)
        # Which should be a list of errors
        self.assertIsInstance(resp_json['errors'], list)
        # With exactly 1 error
        self.assertEqual(len(resp_json['errors']), 1)
        error = resp_json['errors'][0]
        # Which has exactly two fields
        self.assertCountEqual(['code', 'message'], error)
        # The code should be a snake_case string
        self.assertTrue(re.match('[a-zA-Z]+(_[a-zA-Z]+)*', error['code']))
        # The message should be more detailed (e.g. not be a short string)
        self.assertGreater(len(error['message']), 15)

    def test_get_model_fails_with_non_uuid(self) -> None:
        resp = self._test_client.get('/models/some-random-string')
        self.assertEqual(resp.status_code, 422)

    def test_delete_model(self) -> None:
        model = Model.new_model()
        self._test_client.app.state.model_store[str(model.id)] = model
        response = self._test_client.get(f'/models/{str(model.id)}')
        # Check we can get the model
        self.assertEqual(response.status_code, 200)
        delete_resp = self._test_client.delete(f'/models/{str(model.id)}')
        self.assertEqual(delete_resp.status_code, 204)
        # We should no longer be able to retrieve the model
        get_resp = self._test_client.get(f'/models/{str(model.id)}')
        self.assertEqual(get_resp.status_code, 404)

    def test_delete_model_fails_with_non_uuid(self) -> None:
        resp = self._test_client.delete('/models/some-random-string')
        self.assertEqual(resp.status_code, 422)

    def test_delete_model_fails_with_fake_model(self) -> None:
        random_uuid = uuid.uuid4()
        self.assertNotIn(random_uuid, self._test_client.app.state.model_store)
        response = self._test_client.delete(f'/models/{random_uuid}')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
