"""
Unit tests for Grade routes (create-style with POST and GET).
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.grade_routes import create_grade_routes


class TestGradeRoutes(unittest.TestCase):
    """Test cases for Grade routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_grade_routes(),
            url_prefix="/api/grade",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.grade_routes.create_flask_token")
    @patch("src.routes.grade_routes.create_flask_breadcrumb")
    @patch("src.routes.grade_routes.GradeService.create_grade")
    @patch("src.routes.grade_routes.GradeService.get_grade")
    def test_create_grade_success(
        self,
        mock_get_grade,
        mock_create_grade,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/grade for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_grade.return_value = "123"
        mock_get_grade.return_value = {
            "_id": "123",
            "name": "test-grade",
            "status": "active",
        }

        response = self.client.post(
            "/api/grade",
            json={"name": "test-grade", "status": "active"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_create_grade.assert_called_once()
        mock_get_grade.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.grade_routes.create_flask_token")
    @patch("src.routes.grade_routes.create_flask_breadcrumb")
    @patch("src.routes.grade_routes.GradeService.get_grades")
    def test_get_grades_success(
        self,
        mock_get_grades,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/grade for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_grades.return_value = {
            "items": [
                {"_id": "123", "name": "grade1"},
                {"_id": "456", "name": "grade2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/grade")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_grades.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.grade_routes.create_flask_token")
    @patch("src.routes.grade_routes.create_flask_breadcrumb")
    @patch("src.routes.grade_routes.GradeService.get_grade")
    def test_get_grade_success(
        self,
        mock_get_grade,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/grade/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_grade.return_value = {
            "_id": "123",
            "name": "grade1",
        }

        response = self.client.get("/api/grade/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_grade.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.grade_routes.create_flask_token")
    @patch("src.routes.grade_routes.create_flask_breadcrumb")
    @patch("src.routes.grade_routes.GradeService.get_grade")
    def test_get_grade_not_found(
        self,
        mock_get_grade,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/grade/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_grade.side_effect = HTTPNotFound(
            "Grade 999 not found"
        )

        response = self.client.get("/api/grade/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Grade 999 not found")

    @patch("src.routes.grade_routes.create_flask_token")
    def test_create_grade_unauthorized(self, mock_create_token):
        """Test POST /api/grade when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.post(
            "/api/grade",
            json={"name": "test"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
