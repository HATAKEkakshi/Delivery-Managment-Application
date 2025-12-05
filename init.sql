-- Initialize database with required extensions and initial data

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create initial database schema will be handled by SQLModel/Alembic
-- This file can be used for initial data seeding

-- Example: Insert initial tags
-- INSERT INTO tag (id, name, instruction) VALUES 
--     (uuid_generate_v4(), 'express', 'Handle with priority - express delivery'),
--     (uuid_generate_v4(), 'fragile', 'Handle with care - fragile items'),
--     (uuid_generate_v4(), 'heavy', 'Heavy package - use appropriate equipment')
-- ON CONFLICT (name) DO NOTHING;

-- You can add more initialization SQL here