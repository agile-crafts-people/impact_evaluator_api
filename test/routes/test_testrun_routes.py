"""
Unit tests for TestRun routes.

These tests validate the Flask route layer for the TestRun domain, using the
generated blueprint factory and mocking out the underlying service and
token/breadcrumb helpers from api_utils.
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.testrun_routes import create_testrun_routes


class TestTestRunRoutes(unittest.TestCase):
    """Test cases for TestRun routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_testrun_routes(),
            url_prefix="/api/testrun",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.testrun_routes.create_flask_token")
    @patch("src.routes.testrun_routes.create_flask_breadcrumb")
    @patch("src.routes.testrun_routes.TestRunService.create_testrun")
    @patch("src.routes.testrun_routes.TestRunService.get_testrun")
    def test_create_testrun_success(
        self,
        mock_get_testrun,
        mock_create_testrun,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/testrun for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_testrun.return_value = "123"
        mock_get_testrun.return_value = {
            "_id": "123",
            "name": "test-testrun",
            "status": "active",
        }

        response = self.client.post(
            "/api/testrun",
            json={"name": "test-testrun", "status": "active"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_create_testrun.assert_called_once()
        mock_get_testrun.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.testrun_routes.create_flask_token")
    @patch("src.routes.testrun_routes.create_flask_breadcrumb")
    @patch("src.routes.testrun_routes.TestRunService.get_testruns")
    def test_get_testruns_no_filter(
        self,
        mock_get_testruns,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/testrun without name filter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_testruns.return_value = {
            "items": [
                {"_id": "123", "name": "testrun1"},
                {"_id": "456", "name": "testrun2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/testrun")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_testruns.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.testrun_routes.create_flask_token")
    @patch("src.routes.testrun_routes.create_flask_breadcrumb")
    @patch("src.routes.testrun_routes.TestRunService.get_testruns")
    def test_get_testruns_with_name_filter(
        self,
        mock_get_testruns,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/testrun with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_testruns.return_value = {
            "items": [{"_id": "123", "name": "test-testrun"}],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/testrun?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        mock_get_testruns.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name="test",
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.testrun_routes.create_flask_token")
    @patch("src.routes.testrun_routes.create_flask_breadcrumb")
    @patch("src.routes.testrun_routes.TestRunService.get_testrun")
    def test_get_testrun_success(
        self,
        mock_get_testrun,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/testrun/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_testrun.return_value = {
            "_id": "123",
            "name": "testrun1",
        }

        response = self.client.get("/api/testrun/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_testrun.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.testrun_routes.create_flask_token")
    @patch("src.routes.testrun_routes.create_flask_breadcrumb")
    @patch("src.routes.testrun_routes.TestRunService.get_testrun")
    def test_get_testrun_not_found(
        self,
        mock_get_testrun,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/testrun/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_testrun.side_effect = HTTPNotFound(
            "TestRun 999 not found"
        )

        response = self.client.get("/api/testrun/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "TestRun 999 not found")

    @patch("src.routes.testrun_routes.create_flask_token")
    def test_create_testrun_unauthorized(self, mock_create_token):
        """Test POST /api/testrun when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.post(
            "/api/testrun",
            json={"name": "test"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
