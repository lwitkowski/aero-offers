export PYTHONPATH=$PYTHONPATH':./'

set -e

pylint --fail-on=E --errors-only ./