import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import jwt
from app import create_app

class CategoryEndpointTests(unittest.TestCase):
    """Unit tests for category endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        # Generate JWT for admin user
        cls.jwt_secret = "your-secret-key"
        cls.admin_token_payload = {
            "user_id": 1,
            "session_id": "test_session",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "roles": ["admin"]
        }
        cls.admin_token = jwt.encode(cls.admin_token_payload, cls.jwt_secret, algorithm="HS256")

    def setUp(self):
        self.valid_category_data = {
            "name": "Technology"
        }

    @patch("api.v1.categories.get_db")
    def test_create_category_success(self, mock_get_db):
        """Test successful category creation."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_get_db.return_value = iter([mock_db])

        response = self.client.post(
            "/api/v1/categories/",
            json=self.valid_category_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()
        self.assertIn("id", response_data)
        self.assertEqual(response_data["name"], self.valid_category_data["name"])

    @patch("api.v1.categories.get_db")
    def test_create_category_duplicate(self, mock_get_db):
        """Test category creation with duplicate name."""
        mock_db = MagicMock()
        mock_category = MagicMock(id=1, name="Technology")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_category
        mock_get_db.return_value = iter([mock_db])

        response = self.client.post(
            "/api/v1/categories/",
            json=self.valid_category_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 409)
        response_data = response.get_json()
        self.assertIn("error", response_data)

    @patch("api.v1.categories.get_db")
    def test_update_category_success(self, mock_get_db):
        """Test successful category update."""
        mock_db = MagicMock()
        mock_category = MagicMock(id=1, name="Technology")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_category
        mock_get_db.return_value = iter([mock_db])

        update_data = {"name": "Advanced Technology"}

        response = self.client.put(
            "/api/v1/categories/1",
            json=update_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data["name"], update_data["name"])

    @patch("api.v1.categories.get_db")
    def test_delete_category_success(self, mock_get_db):
        """Test successful category deletion."""
        mock_db = MagicMock()
        mock_category = MagicMock(id=1, name="Technology")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_category
        mock_get_db.return_value = iter([mock_db])

        response = self.client.delete(
            "/api/v1/categories/1",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 204)

    @patch("api.v1.categories.get_db")
    def test_get_all_categories(self, mock_get_db):
        """Test retrieving all categories."""
        mock_db = MagicMock()
        mock_categories = [
            MagicMock(id=i, name=f"Category {i}") for i in range(1, 6)
        ]
        mock_db.query.return_value.all.return_value = mock_categories
        mock_get_db.return_value = iter([mock_db])

        response = self.client.get(
            "/api/v1/categories/",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn("categories", response_data)
        self.assertEqual(len(response_data["categories"]), 5)
        self.assertEqual(response_data["categories"][0]["name"], "Category 1")

if __name__ == "__main__":
    unittest.main()
