import unittest
from unittest.mock import patch, MagicMock
from app import create_app
import jwt
from datetime import datetime, timedelta
import os

# Define JWT_SECRET for testing
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")

class TestPostEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the Flask app for testing."""
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.valid_token = cls._generate_valid_token(user_id=1, session_id="12345")

    @staticmethod
    def _generate_valid_token(user_id, session_id):
        """Generate a valid JWT token for testing."""
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    def setUp(self):
        """Initialize test data."""
        self.headers = {"Authorization": f"Bearer {self.valid_token}"}
        self.valid_post_data = {
            "title": "Test Post",
            "content": "This is a test post.",
            "category_id": 1,
            "tags": ["test", "unittest"],
            "status": "draft",
        }
        self.update_post_data = {
            "title": "Updated Test Post",
            "content": "This is an updated test post.",
            "status": "published",
        }

    @patch("api.v1.posts.get_db")
    def test_create_post_success(self, mock_get_db):
        """Test successful post creation."""
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        response = self.client.post(
            "/api/v1/posts/", json=self.valid_post_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())
        self.assertIn("slug", response.get_json())

    @patch("api.v1.posts.get_db")
    def test_create_post_duplicate_slug(self, mock_get_db):
        """Test post creation with duplicate slug."""
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_db.query.return_value.filter_by.return_value.first.return_value = MagicMock(
            slug="test-post"
        )

        response = self.client.post(
            "/api/v1/posts/", json=self.valid_post_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("error", response.get_json())
        self.assertEqual(
            response.get_json()["error"], "A post with this title already exists."
        )

    @patch("api.v1.posts.get_db")
    def test_get_post_success(self, mock_get_db):
        """Test successful retrieval of a post."""
        mock_post = MagicMock(
            id=1,
            title="Test Post",
            content="This is a test post.",
            slug="test-post",
            view_count=0,
            like_count=0,
            category=MagicMock(id=1, name="Test Category"),
            tags=[MagicMock(name="test"), MagicMock(name="unittest")],
        )
        mock_db = MagicMock()
        mock_db.query.return_value.get.return_value = mock_post
        mock_get_db.return_value = iter([mock_db])

        response = self.client.get("/api/v1/posts/1", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["title"], "Test Post")

    @patch("api.v1.posts.get_db")
    def test_update_post_success(self, mock_get_db):
        """Test successful post update."""
        mock_post = MagicMock(
            id=1,
            title="Test Post",
            content="This is a test post.",
            status="draft",
        )
        mock_db = MagicMock()
        mock_db.query.return_value.get.return_value = mock_post
        mock_get_db.return_value = iter([mock_db])

        response = self.client.put(
            "/api/v1/posts/1", json=self.update_post_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.get_json())
        self.assertEqual(
            response.get_json()["message"], "Post updated successfully."
        )

    @patch("api.v1.posts.get_db")
    def test_delete_post_success(self, mock_get_db):
        """Test successful post deletion."""
        mock_post = MagicMock(id=1)
        mock_db = MagicMock()
        mock_db.query.return_value.get.return_value = mock_post
        mock_get_db.return_value = iter([mock_db])

        response = self.client.delete("/api/v1/posts/1", headers=self.headers)
        self.assertEqual(response.status_code, 204)

    @patch("api.v1.posts.get_db")
    def test_get_all_posts_pagination(self, mock_get_db):
        """Test retrieving paginated posts."""
        mock_post1 = MagicMock(
            id=1, title="Post 1", slug="post-1", content="Content 1"
        )
        mock_post2 = MagicMock(
            id=2, title="Post 2", slug="post-2", content="Content 2"
        )
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_post1,
            mock_post2,
        ]
        mock_get_db.return_value = iter([mock_db])

        response = self.client.get("/api/v1/posts/?page=1&size=2", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["title"], "Post 1")
        self.assertEqual(data[1]["title"], "Post 2")


if __name__ == "__main__":
    unittest.main()

