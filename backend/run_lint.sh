export PYTHONPATH=$PYTHONPATH':./src'

set -e

pylint --fail-on=E --errors-only ./