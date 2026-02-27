"""
Unit tests for TestData routes.

These tests validate the Flask route layer for the TestData domain, using the
generated blueprint factory and mocking out the underlying service and
token/breadcrumb helpers from api_utils.
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.testdata_routes import create_testdata_routes


class TestTestDataRoutes(unittest.TestCase):
    """Test cases for TestData routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_testdata_routes(),
            url_prefix="/api/testdata",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.testdata_routes.create_flask_token")
    @patch("src.routes.testdata_routes.create_flask_breadcrumb")
    @patch("src.routes.testdata_routes.TestDataService.create_testdata")
    @patch("src.routes.testdata_routes.TestDataService.get_testdata")
    def test_create_testdata_success(
        self,
        mock_get_testdata,
        mock_create_testdata,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/testdata for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_testdata.return_value = "123"
        mock_get_testdata.return_value = {
            "_id": "123",
            "name": "test-testdata",
            "status": "active",
        }

        response = self.client.post(
            "/api/testdata",
            json={"name": "test-testdata", "status": "active"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_create_testdata.assert_called_once()
        mock_get_testdata.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.testdata_routes.create_flask_token")
    @patch("src.routes.testdata_routes.create_flask_breadcrumb")
    @patch("src.routes.testdata_routes.TestDataService.get_testdatas")
    def test_get_testdatas_no_filter(
        self,
        mock_get_testdatas,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/testdata without name filter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_testdatas.return_value = {
            "items": [
                {"_id": "123", "name": "testdata1"},
                {"_id": "456", "name": "testdata2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/testdata")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_testdatas.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.testdata_routes.create_flask_token")
    @patch("src.routes.testdata_routes.create_flask_breadcrumb")
    @patch("src.routes.testdata_routes.TestDataService.get_testdatas")
    def test_get_testdatas_with_name_filter(
        self,
        mock_get_testdatas,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/testdata with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_testdatas.return_value = {
            "items": [{"_id": "123", "name": "test-testdata"}],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/testdata?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        mock_get_testdatas.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name="test",
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.testdata_routes.create_flask_token")
    @patch("src.routes.testdata_routes.create_flask_breadcrumb")
    @patch("src.routes.testdata_routes.TestDataService.get_testdata")
    def test_get_testdata_success(
        self,
        mock_get_testdata,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/testdata/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_testdata.return_value = {
            "_id": "123",
            "name": "testdata1",
        }

        response = self.client.get("/api/testdata/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_testdata.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.testdata_routes.create_flask_token")
    @patch("src.routes.testdata_routes.create_flask_breadcrumb")
    @patch("src.routes.testdata_routes.TestDataService.get_testdata")
    def test_get_testdata_not_found(
        self,
        mock_get_testdata,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/testdata/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_testdata.side_effect = HTTPNotFound(
            "TestData 999 not found"
        )

        response = self.client.get("/api/testdata/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "TestData 999 not found")

    @patch("src.routes.testdata_routes.create_flask_token")
    def test_create_testdata_unauthorized(self, mock_create_token):
        """Test POST /api/testdata when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.post(
            "/api/testdata",
            json={"name": "test"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
