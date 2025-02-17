docker build . -t aerooffers-db-local:latest
docker run \
  -e "COSMOSDB_URL=https://aerooffers-cosmosdb.documents.azure.com:443/" \
  -e "COSMOSDB_CREDENTIAL=??" \
  aerooffers-db-local:latest \
  sh ./run_update_offers.sh
