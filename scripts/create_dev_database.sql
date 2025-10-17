/*
This file is used to bootstrap development database locally.

Note: ONLY development database;
*/

-- Create role `pareri` with password and CREATEDB, idempotently
DO
$$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_roles WHERE rolname = 'pareri'
	) THEN
		PERFORM 1 FROM pg_catalog.pg_roles; -- no-op to keep block structure
		EXECUTE 'CREATE ROLE pareri WITH LOGIN PASSWORD ''pareri'' CREATEDB';
	ELSE
		-- Ensure password and CREATEDB are set if role already exists
		EXECUTE 'ALTER ROLE pareri WITH LOGIN PASSWORD ''pareri'' CREATEDB';
	END IF;
END
$$;

-- Create database `pareri` owned by `pareri` with UTF8 encoding, if not exists
DO
$$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_database WHERE datname = 'pareri'
	) THEN
		EXECUTE 'CREATE DATABASE pareri OWNER pareri ENCODING ''UTF8''';
	END IF;
END
$$;

-- Optional: grant all privileges on database to owner explicitly (no-op if already owner)
GRANT ALL PRIVILEGES ON DATABASE "pareri" TO "pareri";
