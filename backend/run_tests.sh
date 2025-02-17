set -e

coverage run -m pytest --junit-xml=./test-results.xml
coverage html
