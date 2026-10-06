import importlib
import os
import unittest
from unittest.mock import MagicMock, patch
from uuid import UUID


class FetchAndStoreProxiesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The service imports database configuration at module load time.
        test_environment = {
            "PROXY_USERNAME": "test-user",
            "PASSWORD": "test-password",
            "POSTGRES_USER": "test-user",
            "POSTGRES_PASSWORD": "test-password",
        }
        with patch.dict(os.environ, test_environment):
            cls.service = importlib.import_module("services.proxy_service")

    def setUp(self):
        self.response = MagicMock()
        self.response_context = MagicMock()
        self.response_context.__enter__.return_value = self.response
        self.response_context.__exit__.return_value = False

        self.session = MagicMock()
        self.session_context = MagicMock()
        self.session_context.__enter__.return_value = self.session
        self.session_context.__exit__.return_value = False

    def test_fetches_deduplicates_and_stores_valid_proxies(self):
        self.response.read.return_value = (
            b"http://127.0.0.1:8080\n"
            b"\n"
            b"invalid-proxy\n"
            b"http://127.0.0.1:8080\n"
            b"http://10.0.0.1:3128\n"
        )
        run_uuid = UUID("12345678-1234-5678-1234-567812345678")

        with (
            patch.object(
                self.service, "urlopen", return_value=self.response_context
            ) as urlopen,
            patch.object(
                self.service, "get_session", return_value=self.session_context
            ),
            patch.object(self.service.uuid, "uuid4", return_value=run_uuid),
        ):
            run_id = self.service.fetch_and_store_proxies()

        self.assertEqual(run_id, f"run_{run_uuid}")
        urlopen.assert_called_once_with(
            self.service.PROXY_API_URL,
            timeout=self.service.REQUEST_TIMEOUT_SECONDS,
        )
        stored_proxies = [
            call.args[0] for call in self.session.add.call_args_list
        ]
        self.assertEqual(
            [(proxy.proxy, proxy.dag_run_id) for proxy in stored_proxies],
            [
                ("http://127.0.0.1:8080", run_id),
                ("http://10.0.0.1:3128", run_id),
            ],
        )
        self.session.commit.assert_called_once_with()
        self.session.rollback.assert_not_called()

    def test_raises_when_api_returns_no_valid_proxies(self):
        self.response.read.return_value = b"\ninvalid-proxy\nhttps://example.com:443\n"

        with (
            patch.object(
                self.service, "urlopen", return_value=self.response_context
            ),
            patch.object(self.service, "get_session") as get_session,
            self.assertRaisesRegex(
                RuntimeError, "The proxy API returned no valid HTTP proxies"
            ),
        ):
            self.service.fetch_and_store_proxies()

        get_session.assert_not_called()

    def test_rolls_back_and_reraises_when_database_commit_fails(self):
        self.response.read.return_value = b"http://127.0.0.1:8080\n"
        self.session.commit.side_effect = RuntimeError("database unavailable")

        with (
            patch.object(
                self.service, "urlopen", return_value=self.response_context
            ),
            patch.object(
                self.service, "get_session", return_value=self.session_context
            ),
            self.assertRaisesRegex(RuntimeError, "database unavailable"),
        ):
            self.service.fetch_and_store_proxies()

        self.session.add.assert_called_once()
        self.session.rollback.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
