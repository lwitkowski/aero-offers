export PYTHONPATH=$PYTHONPATH':./src:./tests'

set -e

pylint --fail-on=E --errors-only --ignore venv ./