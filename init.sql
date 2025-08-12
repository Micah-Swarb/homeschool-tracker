-- Initialize Homeschool Hub Database
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create initial admin user (password: admin123)
-- This will be created by the Flask application on first run
-- The script just ensures the database is ready

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE homeschool_hub TO homeschool_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO homeschool_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO homeschool_user;

