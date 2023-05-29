import random
import re
import unittest
import uuid
from typing import Any

from fastapi.testclient import TestClient

from app.api.resources import Status
from app.store import ModelStore
from app.main import app


class TestGetResults(unittest.TestCase):
    _test_client: TestClient = None

    def _check_error_response(self, response_json: dict[Any, Any]) -> None:
        # There should be an "errors" field
        self.assertIn('errors', response_json)
        # Which should be a list of errors
        self.assertIsInstance(response_json['errors'], list)
        # With exactly 1 error
        self.assertEqual(len(response_json['errors']), 1)
        error = response_json['errors'][0]
        # Which has exactly two fields
        self.assertCountEqual(['code', 'message'], error)
        # The code should be a snake_case string
        self.assertTrue(re.match('[a-zA-Z]+(_[a-zA-Z]+)*', error['code']))

    @classmethod
    def setUpClass(cls) -> None:
        random.seed(10)
        cls._test_client = TestClient(app)

    def tearDown(self) -> None:
        # Reset the model store after each test
        self._test_client.app.state.model_store = ModelStore()

    def test_get_results(self) -> None:
        # Create a model
        model_config = {'config': {'data_source': 'https://myexampleapi.com', 'data_api_key': 'my_example_api_key'}}
        response = self._test_client.post('/models', json=model_config)
        # Check the model was created successfully
        self.assertEqual(response.status_code, 201)
        model_id = response.json()['id']
        # Manually update the status
        self._test_client.app.state.model_store.set_status(model_id, Status.COMPLETED)
        # Check the model status has been updated properly
        get_resp = self._test_client.get(f'/models/{model_id}')
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json()['status'], 'completed')
        # Get the results
        results = self._test_client.get(f'/models/{model_id}/results')
        self.assertEqual(results.status_code, 200)
        results_json = results.json()
        # There should be only 1 key in the results
        self.assertCountEqual(['results'], results_json)
        # There should be 3 keys within results
        self.assertCountEqual(['cluster_count', 'total_data_points', 'clusters'], results_json['results'])
        # There should be only 1 cluster
        self.assertEqual(results_json['results']['cluster_count'], 1)
        # With 440 data points
        self.assertEqual(results_json['results']['total_data_points'], 440)
        # Each cluster should have the 3 required keys
        self.assertCountEqual(['cluster_label', 'occurrences', 'members'], results_json['results']['clusters'][0])
        # The cluster should have a label of 0 and contain all 440 total_data_points
        self.assertEqual(len(results_json['results']['clusters']), 1)
        self.assertEqual(results_json['results']['clusters'][0]['cluster_label'], 0)
        self.assertEqual(results_json['results']['clusters'][0]['occurrences'], 440)

    def test_get_results_fails_with_fake_model(self) -> None:
        resp = self._test_client.get(f'/models/{uuid.uuid4()}/results')
        self.assertEqual(resp.status_code, 404)
        resp_json = resp.json()
        self._check_error_response(resp_json)

    def test_get_results_fails_with_non_uuid(self) -> None:
        resp = self._test_client.get('/models/87ebe5ak-f3ez-4d2c-93be-ee600596c397')
        self.assertEqual(resp.status_code, 422)

    def test_get_results_fails_with_incomplete_model(self) -> None:
        # Create a model
        model_config = {'config': {'data_source': 'https://myexampleapi.com', 'data_api_key': 'my_example_api_key'}}
        response = self._test_client.post('/models', json=model_config)
        # Check the model was created successfully
        self.assertEqual(response.status_code, 201)
        model_id = response.json()['id']
        # Should get a Bad Request response when the model is still pending
        results_resp = self._test_client.get(f'/models/{model_id}/results')
        self.assertEqual(results_resp.status_code, 400)
        self._check_error_response(results_resp.json())
        # Manually update the status to RUNNING
        self._test_client.app.state.model_store.set_status(model_id, Status.RUNNING)
        # Check the status updated successfully
        self.assertEqual(self._test_client.get(f'/models/{model_id}').json()['status'], 'running')
        # Re-fetch the results
        results_resp = self._test_client.get(f'/models/{model_id}/results')
        # Should still get an error response as there are no results for a running model
        self.assertEqual(results_resp.status_code, 400)
        self._check_error_response(results_resp.json())
        # Change the status to failed
        self._test_client.app.state.model_store.set_status(model_id, Status.FAILED)
        # Check the status updated successfully
        self.assertEqual(self._test_client.get(f'/models/{model_id}').json()['status'], 'failed')
        # Re-fetch the results
        results_resp = self._test_client.get(f'/models/{model_id}/results')
        # There should be no results for a failed model
        self.assertEqual(results_resp.status_code, 400)
        self._check_error_response(results_resp.json())


if __name__ == '__main__':
    unittest.main()
