export PYTHONPATH=$PYTHONPATH':./'

python3 -m xmlrunner -o ./test-results

if [[ $? -ne 0 ]]; then
    exit 1
fi