docker build . -t aerooffers-local:latest
docker run \
  -p '8085:80' \
  -e "COSMOSDB_URL=https://aerooffers-cosmosdb.documents.azure.com:443/" \
  -e "COSMOSDB_CREDENTIAL=??" \
  aerooffers-local:latest
