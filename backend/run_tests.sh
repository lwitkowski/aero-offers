export PYTHONPATH=$PYTHONPATH':./'

export DB_PORT=35432

docker run \
    --name test-db \
    -d \
    -e 'POSTGRES_DB=aircraft_offers' \
    -e 'POSTGRES_USER=aircraft_offers' \
    -e 'POSTGRES_PASSWORD=aircraft_offers' \
    -p ${DB_PORT}':5432' \
    -v ${PWD}'/../db/ddl.sql:/docker-entrypoint-initdb.d/ddl.sql' \
    postgres:15-alpine

python3 -m unittest

docker rm -f test-db