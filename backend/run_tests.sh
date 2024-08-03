export PYTHONPATH=$PYTHONPATH':./'

set -e

coverage run --source ./ --omit="tests/*" -m xmlrunner -o ./test-results
coverage report --fail-under=65