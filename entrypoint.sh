#!/usr/bin/env bash
# Bring the database schema up to date, then hand off to the container command.
set -euo pipefail

alembic upgrade head
exec "$@"
