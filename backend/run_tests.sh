PYTHONPATH=$PYTHONPATH src pytest tests

set -e

coverage run --source ./ --omit="tests/*" -m xmlrunner -o ./test-results
coverage report --fail-under=70