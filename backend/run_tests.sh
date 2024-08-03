export PYTHONPATH=$PYTHONPATH':./'

coverage run --source ./ -m xmlrunner -o ./test-results

if [[ $? -ne 0 ]]; then
    exit 1
else
  coverage report --fail-under=75
fi