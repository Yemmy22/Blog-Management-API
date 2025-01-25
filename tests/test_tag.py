import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import jwt
from app import create_app

class TagEndpointTests(unittest.TestCase):
    """Unit tests for tag endpoints."""

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
        self.valid_tag_data = {
            "name": "Python",
            "slug": "python"
        }

    @patch("api.v1.tags.get_db")
    def test_create_tag_success(self, mock_get_db):
        """Test successful tag creation."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_get_db.return_value = iter([mock_db])

        response = self.client.post(
            "/api/v1/tags/",
            json=self.valid_tag_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()
        self.assertIn("id", response_data)
        self.assertEqual(response_data["name"], self.valid_tag_data["name"])

    @patch("api.v1.tags.get_db")
    def test_create_tag_duplicate(self, mock_get_db):
        """Test tag creation with duplicate name or slug."""
        mock_db = MagicMock()
        mock_tag = MagicMock(id=1, name="Python", slug="python")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_tag
        mock_get_db.return_value = iter([mock_db])

        response = self.client.post(
            "/api/v1/tags/",
            json=self.valid_tag_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 409)
        response_data = response.get_json()
        self.assertIn("error", response_data)

    @patch("api.v1.tags.get_db")
    def test_update_tag_success(self, mock_get_db):
        """Test successful tag update."""
        mock_db = MagicMock()
        mock_tag = MagicMock(id=1, name="Python", slug="python")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_tag
        mock_get_db.return_value = iter([mock_db])

        update_data = {"name": "Advanced Python", "slug": "advanced-python"}

        response = self.client.put(
            "/api/v1/tags/1",
            json=update_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data["name"], update_data["name"])
        self.assertEqual(response_data["slug"], update_data["slug"])

    @patch("api.v1.tags.get_db")
    def test_delete_tag_success(self, mock_get_db):
        """Test successful tag deletion."""
        mock_db = MagicMock()
        mock_tag = MagicMock(id=1, name="Python", slug="python")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_tag
        mock_get_db.return_value = iter([mock_db])

        response = self.client.delete(
            "/api/v1/tags/1",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 204)

    @patch("api.v1.tags.get_db")
    def test_get_all_tags(self, mock_get_db):
        """Test retrieving all tags."""
        mock_db = MagicMock()
        mock_tags = [
            MagicMock(id=i, name=f"Tag {i}", slug=f"tag-{i}") for i in range(1, 6)
        ]
        mock_db.query.return_value.all.return_value = mock_tags
        mock_get_db.return_value = iter([mock_db])

        response = self.client.get(
            "/api/v1/tags/",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn("tags", response_data)
        self.assertEqual(len(response_data["tags"]), 5)
        self.assertEqual(response_data["tags"][0]["name"], "Tag 1")

if __name__ == "__main__":
    unittest.main()
