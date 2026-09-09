set shell := ["/bin/bash", "-eu", "-o", "pipefail", "-c"]

default:
    @just --list

# Create/update the uv environment with development tools.
setup:
    uv sync --all-groups

# Run the test suite.
test:
    uv run pytest -q

# Check Python code with Ruff.
lint:
    uv run ruff check .

# Format Python code with Ruff.
format:
    uv run ruff format .

# Verify formatting without changing files.
format-check:
    uv run ruff format --check .

# Run all local checks.
check: format-check lint test

# Decode packets from the dongle's serial stream.
sniff port group="20" baud="115200" frequency="7":
    uv run --extra serial radio-bridge sniff --port "{{port}}" --baud "{{baud}}" --group "{{group}}" --frequency "{{frequency}}"
