import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import jwt
import os
from app import create_app
from models.post import PostStatus
from models.user import User
from models.category import Category
from models.tag import Tag

class PostEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.jwt_secret = "your-secret-key"  # Ensure this matches auth.py

    def setUp(self):
        # Create a valid JWT token with realistic mock data
        self.valid_token_payload = {
            "user_id": 1,
            "session_id": "test_session",
            "exp": datetime.utcnow().timestamp() + 3600,
        }
        self.valid_token = jwt.encode(self.valid_token_payload, self.jwt_secret, algorithm="HS256")

        # Sample valid post data with more realistic mock objects
        self.valid_post_data = {
            "title": "Flask Web Development",
            "content": "Comprehensive guide to Flask framework...",
            "category_id": 1,
            "tags": ["python", "web-development"],
            "status": "published",
            "meta_description": "Learn Flask web development",
        }

    @patch("api.v1.posts.get_db")
    @patch("api.v1.auth.redis_client.session_get")
    def test_create_post_success(self, mock_session_get, mock_get_db):
        # Mock session validation
        mock_session_get.return_value = {
            "user_id": 1,
            "username": "testuser",
            "roles": ["author"]
        }

        # Create mock database and objects
        mock_db = MagicMock()
        mock_category = MagicMock(spec=Category, id=1, name="Technology")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_category
        mock_get_db.return_value = iter([mock_db])

        # Send POST request
        response = self.client.post(
            "/api/v1/posts/", 
            json=self.valid_post_data,
            headers={"Authorization": f"Bearer {self.valid_token}"}
        )

        # Assertions
        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()
        self.assertIn("id", response_data)
        self.assertEqual(response_data["title"], self.valid_post_data["title"])

    @patch("api.v1.posts.get_db")
    @patch("api.v1.auth.redis_client.session_get")
    def test_list_posts_pagination(self, mock_session_get, mock_get_db):
        # Mock session validation
        mock_session_get.return_value = {
            "user_id": 1,
            "username": "testuser",
            "roles": ["author"]
        }

        # Create mock posts with concrete data
        mock_db = MagicMock()
        mock_posts = [
            {
                "id": i, 
                "title": f"Post {i}", 
                "slug": f"post-{i}",
                "status": PostStatus.PUBLISHED.value,
                "content": f"Content {i}",
                "author": {"id": 1, "username": "testuser"},
                "category": {"id": 1, "name": "Technology"},
                "tags": [],
                "created_at": datetime.utcnow().isoformat()
            } for i in range(1, 6)
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_posts
        mock_db.query.return_value.filter.return_value.count.return_value = 10
        mock_get_db.return_value = iter([mock_db])

        response = self.client.get(
            "/api/v1/posts/?page=1&per_page=5",
            headers={"Authorization": f"Bearer {self.valid_token}"}
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn("posts", response_data)
        self.assertEqual(len(response_data["posts"]), 5)
        self.assertEqual(response_data["pagination"]["total"], 10)

    # Similar modifications for other test methods...

if __name__ == "__main__":
    unittest.main()
