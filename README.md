# Blog Management API
The Blog Management API is a backend system designed for managing blog platforms. It provides functionality for user authentication, content creation, and organization. This API allows developers to build feature-rich blog applications with secure endpoints, role-based access control, and support for secure scalable and efficient operations.

## Features
The Blog Management API offers a comprehensive set of features tailored for managing blogs and user interactions. Below are its key functionalities:

### Authentication & Authorization
- JWT-based Authentication: Secure login and token-based session management.
- Role-Based Access Control: Fine-grained permission management for roles like author, admin, and moderator.
- Password Security: Passwords are securely hashed and validated using bcrypt.
### Content Management
- Posts: Create, retrieve, update, and delete (CRUD) blog posts.
- Categories: Organize posts into categories with CRUD functionality.
- Tags: Add tags to posts for better content discoverability.
- Comments: Support for threaded comments with moderation options.
### User Management
- Registration & Login: User registration and secure login.
- Session Management: Manage user sessions with Redis.
- Password Reset: Users can request password resets via email.
### Performance & Scalability
- Caching: Redis is used to cache frequently accessed data for faster response times.
- Rate Limiting: Prevent abuse by limiting the number of requests to public endpoints.
### Data Integrity
- Audit Logs: Track user and system activity for compliance and debugging.
- Validation: Comprehensive input validation to ensure data consistency and security.
### Developer-Friendly
- RESTful API: Follows REST principles for predictable and easy-to-use endpoints.
- Pagination: Built-in support for paginated data retrieval.
- Comprehensive Documentation: Every API endpoint is well-documented for ease of integration.

## Purpose
The API is ideal for:

Creating and managing blog posts, categories, and tags.
Supporting multi-role user management (e.g., authors, admins).
Moderating and managing comments.
Providing scalable backend services with caching and rate limiting.
Technology Stack
The API is built using:

Flask: A lightweight Python web framework for building RESTful services.
SQLAlchemy: For database management and ORM (Object Relational Mapping).
Redis: For session management and caching.
bcrypt: For secure password hashing and verification.
JWT: For secure user authentication and authorization.
MySQL: As the relational database system.
Alembic: For database migrations.


## Project Architecture
The Blog Management API is structured to ensure scalability, maintainability, and ease of collaboration. Below is the folder structure along with explanations of its key components:

### Directory Structure
.
├── api/
│   ├── v1/                     # API version 1
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── posts.py            # Endpoints for managing blog posts
│   │   ├── comments.py         # Endpoints for managing comments
│   │   ├── tags.py             # Endpoints for managing tags
│   │   ├── categories.py       # Endpoints for managing categories
│   ├── __init__.py             # API initialization
├── config/
│   ├── database.py             # Database connection and configuration
├── models/
│   ├── user.py                 # User model and related logic
│   ├── post.py                 # Blog post model
│   ├── comment.py              # Comment model
│   ├── tag.py                  # Tag model
│   ├── category.py             # Category model
│   ├── audit_log.py            # Model for tracking system activity
│   ├── user_session.py         # Model for managing user sessions
│   ├── __init__.py             # Database models initialization
├── tests/
│   ├── test_auth.py            # Unit tests for authentication
│   ├── test_post.py            # Unit tests for blog posts
│   ├── test_comment.py         # Unit tests for comments
│   ├── test_tag.py             # Unit tests for tags
│   ├── test_category.py        # Unit tests for categories
├── utils/
│   ├── password.py             # Password hashing and verification utilities
│   ├── redis_client.py         # Redis connection and utilities
│   ├── rate_limiter.py         # Middleware for rate limiting
│   ├── __init__.py             # Utilities initialization
├── validators/
│   ├── validators.py           # Input validation logic
│   ├── __init__.py             # Validators initialization
├── migrations/                 # Database migration scripts (managed by Alembic)
├── app.py                      # Entry point of the application
├── requirements.txt            # Python dependencies
├── init_db.py                  # Database initialization script
└── README.md                   # Project documentation



#####RECHECK#############################################################################################
API (api/)
Contains all the versioned API logic.
Each module represents a resource (e.g., auth, posts, comments).
Models (models/)
Defines the database schema and relationships using SQLAlchemy.
Includes models for users, posts, comments, tags, and more.
Utilities (utils/)
Encapsulates reusable functionality, such as Redis utilities, password hashing, and rate limiting.
Validators (validators/)
Centralized input validation for consistent and secure API handling.
Configuration (config/)
Includes database configurations and connection logic.
Migrations (migrations/)
Stores migration scripts to manage database schema changes over time.
Tests (tests/)
Contains unit tests for all API modules to ensure functionality and prevent regressions.
Entry Point (app.py)
The main file to run the Flask application, initializes the app, and registers all blueprints.


## Setup Instructions
Follow these steps to set up and run the Blog Management API on your local machine.

### Prerequisites
Ensure the following are installed on your system:

- Python: Version 3.8 or higher.
- MySQL: A running MySQL instance for the database.
- Redis: A running Redis instance for session management and caching.
- bycrypt: For password hashing.

	Step 1: Clone the Repository:
		- git clone https://github.com/yourusername/Blog-Management-API.git
		- cd Blog-management-api
	Step 2: Set Up a Virtual Environment
		- python3 -m venv venv
		- source venv/bin/activate  # On Windows: venv\\Scripts\\activate
	
	Step 4: Configure Environment Variables
		FLASK_APP=app.py
		FLASK_ENV=development
		DATABASE_URL=mysql+mysqldb://<username>:<password>@localhost/<database_name>
		JWT_SECRET=your-secret-key
		REDIS_HOST=localhost
		REDIS_PORT=6379
	Step 5: Initialize the Database
		Run the database migration script to set up the schema: `flask db upgrade` or seed the database with 
		initial data by running `python init_db.py`

	Step 6: Start the Redis Server if not already running
		redis-server

	Step 7: Run the Application
		`fask run` or `python app.py`. The API will be accessible at http://127.0.0.1:5000.
	Step 8: Running Unit Tests
		To validate the setup and ensure all features work as expected, run the tests with 
		`python3 -m unittest discover -s tests`

## Usage Guidelines
This section provides instructions on how to interact with the Blog Management API effectively.

	You can interact with the API using tools like:
	- Postman: Create requests with detailed headers, body, and query parameters.
	- cURL: Command-line tool to test API endpoints.
	- Frontend Applications: Integrate this backend with your frontend application.


### Authentication Endpoints

1. Login

URL: /api/v1/auth/login

Method: POST

Description: Authenticates a user and provides a JWT token.

Request Headers:

Content-Type: application/json

Request Body:

{
  "username": "admin",
  "password": "admin123"
}

Response:

{
  "token": "<JWT_TOKEN>",
  "user": {
    "id": 1,
    "username": "admin",
    "roles": ["admin"]
  }
}

Error Response:

401 Unauthorized: Invalid credentials.

403 Forbidden: Inactive account.

2. Logout

URL: /api/v1/auth/logout

Method: POST

Description: Logs out the user by invalidating the session.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Response:

{
  "message": "Logged out successfully"
}

Error Response:

401 Unauthorized: Invalid or missing token.

3. Session Verification

URL: /api/v1/auth/session/verify

Method: GET

Description: Verifies the validity of a JWT token.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Response:

{
  "valid": true
}

Error Response:

401 Unauthorized: Invalid or expired token.

4. Request Password Reset

URL: /api/v1/auth/reset-password

Method: POST

Description: Initiates a password reset request by sending a token to the user's email.

Request Headers:

Content-Type: application/json

Request Body:

{
  "email": "admin@example.com"
}

Response:

{
  "message": "Password reset link sent to email."
}

Error Response:

404 Not Found: Email not associated with any account.

5. Reset Password

	URL: /api/v1/auth/reset-password/<reset_token>

	Method: POST

	Description: Resets the password using a valid reset token.

	Request Headers:

	Content-Type: application/json

	Request Body:

	{	
	  "password": "newpassword123"
	}

	Response:

	{
	  "message": "Password reset successful."
	}

	Error Response:

	400 Bad Request: Invalid or expired token.


6. Authentication Error Codes

	400 Bad Request: Missing or invalid parameters.

	401 Unauthorized: Missing or invalid token.

	403 Forbidden: Access denied.

	404 Not Found: Resource not found.

	409 Conflict: Duplicate resource.


### Post Endpoints

1. Create Post

URL: /api/v1/posts/

Method: POST

Description: Creates a new blog post.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Content-Type: application/json

Request Body:

{
  "title": "Getting Started with Flask",
  "content": "Flask is a lightweight WSGI web application framework...",
  "category_id": 1,
  "tags": ["python", "web-development"],
  "status": "published"
}

Response:

{
  "id": 1,
  "slug": "getting-started-with-flask",
  "status": "published",
  "title": "Getting Started with Flask"
}

Error Response:

400 Bad Request: Missing required fields.

404 Not Found: Category not found.

2. Get All Posts

URL: /api/v1/posts/

Method: GET

Description: Retrieves a paginated list of blog posts.

Query Parameters:

page: Page number (default: 1).

per_page: Number of posts per page (default: 10).

Response:

{
  "posts": [
    {
      "id": 1,
      "title": "Getting Started with Flask",
      "slug": "getting-started-with-flask",
      "status": "published",
      "created_at": "2025-01-01T12:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100
  }
}

Error Response:

500 Internal Server Error: Server issues.

3. Get Post by Slug

URL: /api/v1/posts/<slug>

Method: GET

Description: Retrieves details of a specific post by its slug.

Response:

{
  "id": 1,
  "title": "Getting Started with Flask",
  "slug": "getting-started-with-flask",
  "content": "Flask is a lightweight WSGI web application framework...",
  "status": "published",
  "category": {
    "id": 1,
    "name": "Programming"
  },
  "tags": ["python", "web-development"]
}

Error Response:

404 Not Found: Post not found.

4. Update Post

URL: /api/v1/posts/<slug>

Method: PUT

Description: Updates an existing post.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Content-Type: application/json

Request Body:

{
  "title": "Updated Title",
  "content": "Updated content...",
  "tags": ["updated", "flask"]
}

Response:

{
  "id": 1,
  "slug": "updated-title",
  "status": "published",
  "title": "Updated Title"
}

Error Response:

404 Not Found: Post not found.

5. Delete Post

URL: /api/v1/posts/<slug>

Method: DELETE

Description: Deletes a post by its slug.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Response:

{
  "message": "Post deleted successfully."
}

Error Response:

404 Not Found: Post not found.

6. Error Codes

	400 Bad Request: Missing or invalid parameters.

	401 Unauthorized: Missing or invalid token.

	403 Forbidden: Access denied.

	404 Not Found: Resource not found.

	409 Conflict: Duplicate resource.


### Tag Endpoints

1. Create Tag

URL: /api/v1/tags/

Method: POST

Description: Creates a new tag.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Content-Type: application/json

Request Body:

{
  "name": "python"
}

Response:

{
  "id": 1,
  "name": "python",
  "slug": "python",
  "created_at": "2025-01-01T12:00:00"
}

Error Response:

409 Conflict: Tag with the same name already exists.

2. Get All Tags

URL: /api/v1/tags/

Method: GET

Description: Retrieves all tags.

Response:

{
  "tags": [
    {
      "id": 1,
      "name": "python",
      "slug": "python",
      "created_at": "2025-01-01T12:00:00"
    }
  ]
}

Error Response:

500 Internal Server Error: Server issues.

3. Get Tag by Slug

URL: /api/v1/tags/<slug>

Method: GET

Description: Retrieves details of a specific tag by its slug.

Response:

{
  "id": 1,
  "name": "python",
  "slug": "python",
  "created_at": "2025-01-01T12:00:00"
}

Error Response:

404 Not Found: Tag not found.

4. Update Tag

URL: /api/v1/tags/<slug>

Method: PUT

Description: Updates an existing tag.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Content-Type: application/json

Request Body:

{
  "name": "python-updated"
}

Response:

{
  "id": 1,
  "name": "python-updated",
  "slug": "python-updated",
  "updated_at": "2025-01-01T12:30:00"
}

Error Response:

404 Not Found: Tag not found.

5. Delete Tag

URL: /api/v1/tags/<slug>

Method: DELETE

Description: Deletes a tag by its slug.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Response:

{
  "message": "Tag deleted successfully."
}

Error Response:

404 Not Found: Tag not found.

6. Search Tags

URL: /api/v1/tags/

Method: GET

Description: Retrieves tags based on search criteria.

Query Parameters:

search: Keyword to search for tags.

include_stats: Whether to include tag usage statistics (true/false).

Response:

{
  "tags": [
    {
      "id": 1,
      "name": "python",
      "slug": "python",
      "created_at": "2025-01-01T12:00:00",
      "post_count": 5
    }
  ]
}

Error Response:

500 Internal Server Error: Server issues.

7. Merge Tags

URL: /api/v1/tags/merge

Method: POST

Description: Merges multiple tags into one.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Content-Type: application/json

Request Body:

{
  "source_slugs": ["python", "py"],
  "target_slug": "python-programming"
}

Response:

{
  "message": "Tags merged successfully."
}

Error Response:

404 Not Found: One or more source tags not found.

409 Conflict: Target slug already exists.


Category Endpoints

1. List All Categories

URL: /api/v1/categories/

Method: GET

Description: Retrieves a list of all categories.

Response:

{
  "categories": [
    {
      "id": 1,
      "name": "Technology",
      "created_at": "2025-01-01T12:00:00"
    },
    {
      "id": 2,
      "name": "Programming",
      "created_at": "2025-01-02T14:00:00"
    }
  ]
}

Error Response:

500 Internal Server Error: An error occurred while retrieving categories.

2. Create a Category

URL: /api/v1/categories/

Method: POST

Description: Creates a new category.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Content-Type: application/json

Request Body:

{
  "name": "Technology"
}

Response:

{
  "id": 1,
  "name": "Technology",
  "created_at": "2025-01-01T12:00:00"
}

Error Response:

400 Bad Request: Missing required fields.

409 Conflict: Category with the same name already exists.

3. Get a Category by ID

URL: /api/v1/categories/<id>

Method: GET

Description: Retrieves details of a specific category by its ID.

Response:

{
  "id": 1,
  "name": "Technology",
  "created_at": "2025-01-01T12:00:00"
}

Error Response:

404 Not Found: Category with the specified ID does not exist.

4. Update a Category

URL: /api/v1/categories/<id>

Method: PUT

Description: Updates an existing category.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Content-Type: application/json

Request Body:

{
  "name": "Updated Technology"
}

Response:

{
  "id": 1,
  "name": "Updated Technology",
  "updated_at": "2025-01-05T12:00:00"
}

Error Response:

400 Bad Request: Missing required fields.

404 Not Found: Category with the specified ID does not exist.

409 Conflict: Category with the same name already exists.

5. Delete a Category

URL: /api/v1/categories/<id>

Method: DELETE

Description: Deletes a category by its ID.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Response:

{
  "message": "Category deleted successfully."
}

Error Response:

404 Not Found: Category with the specified ID does not exist.

400 Bad Request: Category cannot be deleted because it is associated with existing posts.



Comment Endpoints

1. Add Comment to a Post

URL: /api/v1/comments/post/<post_id>

Method: POST

Description: Adds a comment to a specific post.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Content-Type: application/json

Request Body:

{
  "content": "This is a new comment.",
  "parent_id": null
}

Response:

{
  "id": 1,
  "post_id": 10,
  "content": "This is a new comment.",
  "user": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2025-01-01T12:00:00"
}

Error Response:

400 Bad Request: Missing required fields.

404 Not Found: Post with the specified ID does not exist.

2. Get Comments for a Post

URL: /api/v1/comments/post/<post_id>

Method: GET

Description: Retrieves all comments associated with a specific post.

Response:

{
  "comments": [
    {
      "id": 1,
      "content": "This is a comment.",
      "user": {
        "id": 1,
        "username": "admin"
      },
      "created_at": "2025-01-01T12:00:00",
      "replies": [
        {
          "id": 2,
          "content": "This is a reply.",
          "user": {
            "id": 2,
            "username": "user1"
          },
          "created_at": "2025-01-01T13:00:00"
        }
      ]
    }
  ]
}

Error Response:

404 Not Found: Post with the specified ID does not exist.

3. Update a Comment

URL: /api/v1/comments/<comment_id>

Method: PUT

Description: Updates an existing comment.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Content-Type: application/json

Request Body:

{
  "content": "This is an updated comment."
}

Response:

{
  "id": 1,
  "content": "This is an updated comment.",
  "updated_at": "2025-01-02T12:00:00"
}

Error Response:

400 Bad Request: Missing required fields.

404 Not Found: Comment with the specified ID does not exist.

4. Delete a Comment

URL: /api/v1/comments/<comment_id>

Method: DELETE

Description: Deletes a comment by its ID.

Request Headers:

Authorization: Bearer <JWT_TOKEN>

Response:

{
  "message": "Comment deleted successfully."
}

Error Response:

404 Not Found: Comment with the specified ID does not exist.

400 Bad Request: Comment cannot be deleted because it has replies.

5. Get Replies for a Comment

URL: /api/v1/comments/replies/<comment_id>

Method: GET

Description: Retrieves replies to a specific comment.

Response:

{
  "replies": [
    {
      "id": 2,
      "content": "This is a reply.",
      "user": {
        "id": 2,
        "username": "user1"
      },
      "created_at": "2025-01-01T13:00:00"
    }
  ]
}

Error Response:

404 Not Found: Comment with the specified ID does not exist.

Notes

All requests requiring authorization must include a valid JWT token in the Authorization header.

Comments and replies can have nested structures, allowing deeper levels of discussion.
