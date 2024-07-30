echo "Starting Postgres docker container"

docker network create test-network

docker run --rm \
    --name test-db \
    -d \
    --network test-network \
    -e 'POSTGRES_DB=aircraft_offers' \
    -e 'POSTGRES_USER=aircraft_offers' \
    -e 'POSTGRES_PASSWORD=aircraft_offers' \
    postgres:16.3-alpine

sleep 2

echo "Running migrations"

docker run --rm \
    --network test-network \
    -v ${PWD}'/migrations/:/flyway/sql' \
    flyway/flyway \
    -url=jdbc:postgresql://test-db:5432/aircraft_offers -user=aircraft_offers -password=aircraft_offers migrate

docker rm -f test-db
docker network rm test-network