-- ============================================================================
-- 02_create_user.sql
-- ----------------------------------------------------------------------------
-- CAVEAT: The GRANT CREATE and ALTER DEFAULT PRIVILEGES statements below must
-- be run by a SUPERUSER or the owner of the database/schema (e.g. the
-- 'postgres' login) — NOT by 'weather_user' itself. A role cannot grant itself
-- privileges it does not already hold.
--
-- Note for PostgreSQL 15+: ordinary users no longer get CREATE on the 'public'
-- schema by default, so the explicit "GRANT ... CREATE ON SCHEMA public" line
-- is required — without it, CREATE TABLE fails with:
--   ERROR: permission denied for schema public (SQLSTATE 42501)
-- ============================================================================

-- Create the user (role)
CREATE USER weather_user WITH PASSWORD 'Skrall2468@';

GRANT CONNECT ON DATABASE weather_forecast TO weather_user;

-- Schema-level: USAGE to enter the schema, CREATE to make new tables
GRANT USAGE, CREATE ON SCHEMA public TO weather_user;

-- Privileges on tables/sequences that already exist at grant time
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO weather_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO weather_user;

-- Privileges on objects created in the future (so you don't have to re-grant)
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO weather_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO weather_user;
