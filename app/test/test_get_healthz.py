import unittest

from fastapi.testclient import TestClient

from app.main import app


class TestGetHealthz(unittest.TestCase):
    _test_client: TestClient = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._test_client = TestClient(app)

    def test_get_healthz(self) -> None:
        response = self._test_client.get('/healthz')
        self.assertEqual(response.status_code, 204)
