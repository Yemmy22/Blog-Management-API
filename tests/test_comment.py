import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import jwt
from app import create_app

class CommentEndpointTests(unittest.TestCase):
    """Unit tests for comment endpoints."""

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
        self.valid_comment_data = {
            "post_id": 1,
            "content": "This is a test comment",
            "parent_id": None
        }

    @patch("api.v1.comments.get_db")
    def test_create_comment_success(self, mock_get_db):
        """Test successful comment creation."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = MagicMock(id=1)
        mock_get_db.return_value = iter([mock_db])

        response = self.client.post(
            "/api/v1/comments/",
            json=self.valid_comment_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()
        self.assertIn("id", response_data)
        self.assertEqual(response_data["content"], self.valid_comment_data["content"])

    @patch("api.v1.comments.get_db")
    def test_update_comment_success(self, mock_get_db):
        """Test successful comment update."""
        mock_db = MagicMock()
        mock_comment = MagicMock(id=1, content="Old content")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_comment
        mock_get_db.return_value = iter([mock_db])

        update_data = {"content": "Updated comment content"}

        response = self.client.put(
            "/api/v1/comments/1",
            json=update_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data["content"], update_data["content"])

    @patch("api.v1.comments.get_db")
    def test_delete_comment_success(self, mock_get_db):
        """Test successful comment deletion."""
        mock_db = MagicMock()
        mock_comment = MagicMock(id=1, content="This is a comment")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_comment
        mock_get_db.return_value = iter([mock_db])

        response = self.client.delete(
            "/api/v1/comments/1",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 204)

    @patch("api.v1.comments.get_db")
    def test_get_all_comments(self, mock_get_db):
        """Test retrieving all comments for a post."""
        mock_db = MagicMock()
        mock_comments = [
            MagicMock(id=i, content=f"Comment {i}", created_at=datetime.utcnow())
            for i in range(1, 6)
        ]
        mock_db.query.return_value.filter_by.return_value.all.return_value = mock_comments
        mock_get_db.return_value = iter([mock_db])

        response = self.client.get(
            "/api/v1/comments/?post_id=1",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn("comments", response_data)
        self.assertEqual(len(response_data["comments"]), 5)
        self.assertEqual(response_data["comments"][0]["content"], "Comment 1")

    @patch("api.v1.comments.get_db")
    def test_create_comment_invalid_post(self, mock_get_db):
        """Test creating a comment for a non-existent post."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_get_db.return_value = iter([mock_db])

        response = self.client.post(
            "/api/v1/comments/",
            json=self.valid_comment_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 404)
        response_data = response.get_json()
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Post not found")

if __name__ == "__main__":
    unittest.main()
