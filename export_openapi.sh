#!/bin/bash

# Exit on error
set -e

# Step 1: Ensure the directory exists and run the export command in the pop-server service
docker compose exec pop-server bash -c "
  mkdir -p /app/data && \
  python manage.py export_openapi --output /app/data/openapi.json --indent 2
"

# Step 2: Copy the file from the container to the host
docker compose cp pop-server:/app/data/openapi.json pop-client/openapi.json

echo "✅ OpenAPI spec exported to pop-client/openapi.json"