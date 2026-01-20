docker build . -t aerooffers-local:latest
docker run \
  -p '8085:8080' \
  --env-file ./.env \
  aerooffers-local:latest
