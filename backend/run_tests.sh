export PYTHONPATH=$PYTHONPATH':./'

set -e

coverage run --source ./ -m xmlrunner -o ./test-results
coverage report --fail-under=80