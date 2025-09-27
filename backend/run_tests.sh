set -e

uv run pytest --cov --cov-fail-under=80 --junit-xml=./test-results.xml
