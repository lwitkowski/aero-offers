docker build . -t aerooffers-db-local:latest
docker run \
  -p '8085:80' \
  -e "COSMOSDB_URL=https://aerooffers-cosmosdb.documents.azure.com:443/" \
  -e "COSMOSDB_CREDENTIAL=??" \
  aerooffers-db-local:latest
