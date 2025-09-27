docker build . -t aerooffers-local:latest
docker run \
  -e "COSMOSDB_URL=https://aerooffers-cosmosdb.documents.azure.com:443/" \
  -e "COSMOSDB_CREDENTIAL=??" \
  aerooffers-local:latest \
  sh ./run_update_offers.sh
