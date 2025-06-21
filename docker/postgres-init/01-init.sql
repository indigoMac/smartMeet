-- SmartMeet PostgreSQL Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Ensure the database exists
SELECT 'CREATE DATABASE smartmeet_dev' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'smartmeet_dev')\gexec

-- Grant all privileges to the smartmeet user
GRANT ALL PRIVILEGES ON DATABASE smartmeet_dev TO smartmeet;

-- Set some PostgreSQL settings for development
ALTER DATABASE smartmeet_dev SET timezone TO 'UTC';
ALTER DATABASE smartmeet_dev SET log_statement TO 'all';

-- Create extensions if they don't exist
\c smartmeet_dev
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Log completion
SELECT 'SmartMeet database initialization completed' AS status; 