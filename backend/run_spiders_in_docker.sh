docker build . -t aerooffers-local:latest
docker run \
  --env-file ./.env.local \
  aerooffers-local:latest \
  sh ./run_update_offers.sh
