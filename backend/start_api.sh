export PYTHONPATH=$PYTHONPATH':./src'

flask --app=./src/api/flask_app.py --debug run --port=8082