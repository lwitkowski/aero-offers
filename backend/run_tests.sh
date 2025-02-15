set -e

coverage run -m pytest --junit-xml=./test-results.xml
coverage html
coverage report --fail-under=80
