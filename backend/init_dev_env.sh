python -m venv ./venv

source venv/bin/activate

pip install --upgrade pip
pip install --quiet -r requirements.txt -r tests/requirements.txt