import unittest
import uuid
import random

from app.api.resources import Model, ResultItem, Status
from app.api.store import ModelStore


class TestModelStore(unittest.TestCase):
    _model_store: ModelStore

    def setUp(self) -> None:
        self._model_store = ModelStore()

    def test_create_new_model(self) -> None:
        model = Model.new_model()
        # Adding a new model should create a key, tuple pair
        self._model_store[str(model.id)] = model
        self.assertIn(str(model.id), self._model_store)
        self.assertIsInstance(self._model_store[str(model.id)], tuple)
        # The results should be None
        self.assertEqual(self._model_store[str(model.id)], (model, None))
        # There should only be 1 model in the ModelStore
        self.assertEqual(len(self._model_store), 1)
        # Trying to re-create or update the same key should result in a KeyError as direct updates are not supported.
        with self.assertRaises(KeyError):
            self._model_store[str(model.id)] = model
        # I should be able to delete an existing model
        del self._model_store[str(model.id)]
        # The model should no longer be in the ModelStore
        self.assertNotIn(str(model.id), self._model_store)

    def test_create_fails_with_mismatched_ids(self) -> None:
        model = Model.new_model()
        # The IDs of the model and the index must match
        with self.assertRaises(ValueError):
            self._model_store[str(uuid.uuid4())] = model

    def test_update_model_status(self) -> None:
        model = Model.new_model()
        self._model_store[str(model.id)] = model
        self.assertIn(str(model.id), self._model_store)
        # Check the status is still pending
        self.assertEqual(self._model_store[str(model.id)][0].status, Status.PENDING)

        self._model_store.set_status(str(model.id), Status.COMPLETED)
        # The status should now be complete
        self.assertEqual(self._model_store[str(model.id)][0].status, Status.COMPLETED)

    def test_store_update_multiple_models(self) -> None:
        # Add multiple models to the ModelStore
        model = Model.new_model()
        self._model_store[str(model.id)] = model
        self.assertIn(str(model.id), self._model_store)
        second_model = Model.new_model()
        self._model_store[str(second_model.id)] = second_model
        self.assertIn(str(second_model.id), self._model_store)
        # There should now be 2 models in the ModelStore
        self.assertEqual(len(self._model_store), 2)
        # We should be able to update the status of both models
        self._model_store.set_status(str(model.id), Status.COMPLETED)
        self._model_store.set_status(str(second_model.id), Status.RUNNING)
        self.assertEqual(self._model_store[str(model.id)][0].status, Status.COMPLETED)
        self.assertEqual(self._model_store[str(second_model.id)][0].status, Status.RUNNING)
        # We should be able to delete one of the models
        del self._model_store[str(model.id)]
        self.assertNotIn(str(model.id), self._model_store)
        self.assertIn(str(second_model.id), self._model_store)

    def test_update_fails_on_complete_model(self) -> None:
        model = Model.new_model()
        self._model_store[str(model.id)] = model
        # Set the Status to complete
        self._model_store.set_status(str(model.id), Status.COMPLETED)
        # It should not be possible to update the status of a completed model
        self.assertRaises(ValueError, self._model_store.set_status, str(model.id), Status.FAILED)

        # It should also not be possible to update the status of a failed model
        failed_model = Model.new_model()
        self._model_store[str(failed_model.id)] = failed_model
        self._model_store.set_status(str(failed_model.id), Status.FAILED)
        self.assertRaises(ValueError, self._model_store.set_status, str(model.id), Status.RUNNING)

    def test_get_results(self) -> None:
        model = Model.new_model()
        self._model_store[str(model.id)] = model
        # There should be no results for a pending model
        self.assertEqual(self._model_store[str(model.id)][0].status, Status.PENDING)
        self.assertIsNone(self._model_store.get_results(str(model.id)))
        # There should be no results for a running model
        self._model_store.set_status(str(model.id), Status.RUNNING)
        self.assertIsNone(self._model_store.get_results(str(model.id)))
        # There should be no results for a failed model
        self._model_store.set_status(str(model.id), Status.FAILED)
        self.assertIsNone(self._model_store.get_results(str(model.id)))
        # There should be some results for a completed model
        model = Model.new_model()
        self._model_store[str(model.id)] = model
        self._model_store.set_status(str(model.id), Status.COMPLETED)

        random.seed(5)
        results = self._model_store.get_results(str(model.id))
        self.assertIsInstance(results, list)
        # There should be 5 clusters
        self.assertEqual(len(results), 8)
        # All elements of results should be a ResultItem
        self.assertTrue(all(isinstance(item, ResultItem) for item in results))
        for cluster_id, cluster in enumerate(results):
            # The cluster IDs should be sequential
            self.assertEqual(cluster.cluster, cluster_id)
            # It doesn't matter how many occurrences/members the cluster has, so long as there is not 0.
            # Although this should be consistent.
            self.assertGreater(len(cluster.members), 0)
            self.assertGreater(cluster.occurrences, 0)
        # The results returned from get_results should match those stored as part of the ModelStore
        self.assertEqual(results, self._model_store[str(model.id)][1])


if __name__ == '__main__':
    unittest.main()
