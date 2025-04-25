#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER showyourheart;
	CREATE DATABASE showyourheart;
	GRANT ALL PRIVILEGES ON DATABASE showyourheart TO showyourheart;
EOSQL
