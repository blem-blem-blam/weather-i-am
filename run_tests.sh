#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting test database container ---"
# Use -f to specify the test compose file
# Use -d to run in the background
# Use --wait to ensure the database is ready to accept connections
docker compose -f docker-compose.test.yml up -d --wait

# This is read as a conditional in our config.py to enable the .env.test file
export TESTING=true

echo "--- Running pytest ---"
poetry run pytest

echo "--- Running pytest coverage ---"
poetry run pytest --cov=app

echo "--- Shutting down test database container ---"
docker compose -f docker-compose.test.yml down

echo "--- Done ---"
