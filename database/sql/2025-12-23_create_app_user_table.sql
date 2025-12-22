-- Create application user table to avoid conflict with Postgres pg_user view
CREATE TABLE IF NOT EXISTS app_user (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NULL REFERENCES pg_property(id) ON DELETE SET NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(254) NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Helpful indexes matching the Django model
CREATE INDEX IF NOT EXISTS idx_app_user_username ON app_user(username);
CREATE INDEX IF NOT EXISTS idx_app_user_email ON app_user(email);
CREATE INDEX IF NOT EXISTS idx_app_user_role ON app_user(role);

-- Note: Django will manage updated_at via auto_now on save. If you prefer DB-side updates,
-- you can add a trigger to set updated_at=NOW() on UPDATE.
