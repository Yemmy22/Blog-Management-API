-- Create the MySQL database
CREATE DATABASE IF NOT EXISTS blog_management 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_general_ci;

-- Create a dedicated user with limited privileges
CREATE USER IF NOT EXISTS 'blog_user'@'localhost' IDENTIFIED BY 'secure_password';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON blog_management.* TO 'blog_user'@'localhost';

-- Ensure changes take effect
FLUSH PRIVILEGES;
