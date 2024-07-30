export PYTHONPATH=$PYTHONPATH':./'

python3 -m unittest -f

if [[ $? -ne 0 ]]; then
    docker rm -f test-db
    exit 1
else
    docker rm -f test-db
fi