export PYTHONPATH=$PYTHONPATH':./'

python3 -m unittest -v

if [[ $? -ne 0 ]]; then
    exit 1
fi