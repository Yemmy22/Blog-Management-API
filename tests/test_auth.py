import unittest
from unittest.mock import patch, MagicMock
import jwt
import bcrypt
from datetime import datetime, timedelta
import os
from app import create_app

class AuthenticationTests(unittest.TestCase):
    """Unit tests for authentication endpoints."""

    @classmethod
    def setUpClass(cls):
        """Set up the Flask app and test client."""
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")

    def setUp(self):
        """Set up test data for individual test cases."""
        self.valid_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePassword123!",
        }
        self.login_credentials = {
            "username": "testuser",
            "password": "SecurePassword123!",
        }

    def _create_mock_user(self, is_active=True):
        """Helper function to create a mock user."""
        hashed_password = bcrypt.hashpw(
            self.login_credentials["password"].encode(), bcrypt.gensalt()
        ).decode()

        return MagicMock(
            id=1,
            username=self.login_credentials["username"],
            email=self.valid_user_data["email"],
            password=hashed_password,
            is_active=is_active,
            roles=[MagicMock(name="user")],
        )

    @patch('utils.redis_client.RedisClient.rate_limit', return_value=True)
    @patch('api.v1.auth.get_db')
    @patch('utils.password.verify_password')
    @patch('utils.redis_client.RedisClient.session_set')
    @patch('jwt.encode')
    def test_successful_login(
        self, mock_jwt_encode, mock_session_set, mock_verify_password, mock_get_db, mock_rate_limit
):
        """Test successful login."""
        # Create mock role object
        mock_role = MagicMock()
        mock_role.name = 'user'

        # Create mock user object with roles as objects having a 'name' attribute
        mock_user = MagicMock(
            id=1,
            username=self.login_credentials['username'],
            email=self.valid_user_data['email'],
            password=bcrypt.hashpw(self.login_credentials['password'].encode(), bcrypt.gensalt()).decode(),
            is_active=True,
            roles=[mock_role]
        )

        # Mock database query to return the mock user
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_get_db.return_value = iter([mock_db])

        # Mock password verification and JWT encoding
        mock_verify_password.return_value = True
        mock_jwt_encode.return_value = 'mock_token'

        # Make the login request
        response = self.client.post('/api/v1/auth/login', json=self.login_credentials)

        # Assert response status and content
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('token', response_data)
        self.assertIn('user', response_data)
        self.assertEqual(response_data['user']['username'], self.login_credentials['username'])


    @patch("utils.redis_client.RedisClient.rate_limit", return_value=True)
    @patch("api.v1.auth.get_db")
    def test_login_inactive_user(self, mock_get_db, mock_rate_limit):
        """Test login with an inactive user."""
        mock_user = self._create_mock_user(is_active=False)
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_get_db.return_value = iter([mock_db])

        response = self.client.post(
            "/api/v1/auth/login", json=self.login_credentials
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["error"], "Account is inactive")

    @patch("utils.redis_client.RedisClient.rate_limit", return_value=True)
    @patch("api.v1.auth.get_db")
    def test_login_invalid_credentials(self, mock_get_db, mock_rate_limit):
        """Test login with invalid credentials."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_get_db.return_value = iter([mock_db])

        response = self.client.post(
            "/api/v1/auth/login", json={"username": "nonexistent", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.get_json())

    @patch("utils.redis_client.RedisClient.rate_limit", return_value=True)
    def test_login_missing_credentials(self, mock_rate_limit):
        """Test login with missing credentials."""
        response = self.client.post("/api/v1/auth/login", json={"password": "test"})
        self.assertEqual(response.status_code, 400)

        response = self.client.post("/api/v1/auth/login", json={"username": "test"})
        self.assertEqual(response.status_code, 400)

    @patch("utils.redis_client.RedisClient.rate_limit", return_value=True)
    @patch("api.v1.auth.get_db")
    def test_password_reset_request(self, mock_get_db, mock_rate_limit):
        """Test password reset request."""
        mock_user = MagicMock(email="test@example.com")
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_get_db.return_value = iter([mock_db])

        response = self.client.post(
            "/api/v1/auth/reset-password", json={"email": "test@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.get_json())

    def test_session_verification(self):
        """Test session verification with a valid token."""
        token_payload = {
            "user_id": 1,
            "session_id": "test_session",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(token_payload, self.jwt_secret, algorithm="HS256")

        with patch(
            "utils.redis_client.RedisClient.session_get", return_value={"user_id": 1}
        ):
            response = self.client.get(
                "/api/v1/auth/session/verify", headers={"Authorization": f"Bearer {token}"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.get_json()["valid"])

    @patch('utils.redis_client.RedisClient.rate_limit', return_value=True)
    @patch('api.v1.auth.get_db')
    @patch('utils.redis_client.RedisClient.session_delete')
    def test_logout_success(self, mock_session_delete, mock_get_db, mock_rate_limit):
        """Test successful logout."""
        # Create a mock user
        mock_user = self._create_mock_user()

        # Mock database query
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        # Mock Redis session delete
        mock_session_delete.return_value = None

        # Create a valid JWT token with session details
        token_payload = {
            'user_id': 1,
            'session_id': 'test_session',
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')

        # Add a mock for session_get to simulate an existing session
        with patch('utils.redis_client.RedisClient.session_get', return_value={'user_id': 1, 'session_id': 'test_session'}):
            # Perform logout request
            headers = {'Authorization': f'Bearer {token}'}
            response = self.client.post('/api/v1/auth/logout', headers=headers)

            self.assertEqual(response.status_code, 200)
            self.assertIn('message', response.get_json())
            self.assertEqual(response.get_json()['message'], 'Logged out successfully')


if __name__ == "__main__":
    unittest.main()

