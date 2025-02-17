RESOURCE_GROUP=rg-aerooffers
LOCATION="Switzerland North"
ENV_NAME=cae-aerooffers-prod
CONTAINER_REGISTRY_SERVER=ghcr.io
CONTAINER_REGISTRY_PASSWORD=???
CONTAINER_REGISTRY=${CONTAINER_REGISTRY_SERVER}/lwitkowski
DOCKER_IMAGE_TAG=???
COSMOSDB_URL=http://localhost:8082
COSMOSDB_CREDENTIAL=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
COSMOSDB_DB_NAME=aerooffers

az group create \
  --name $RESOURCE_GROUP \
  --location "$LOCATION"

az containerapp env create \
  --name $ENV_NAME \
  --resource-group $RESOURCE_GROUP \
  --location "$LOCATION"

az identity create \
  --name id-aerooffers \
  --resource-group $RESOURCE_GROUP \
  --location "$LOCATION"

# assign identity a 'Contributor' role to resource group  'rg-aerooffers'
# create federated credential for identity with subject identifier repo:lwitkowski/aero-offers:environment:production

az staticwebapp create \
    --name aerooffers-ui \
    --resource-group $RESOURCE_GROUP

# now setup custom domain for this app (TXT & A DNS records etc)

# create cosmosdb free tier
az cosmosdb create \
    --name "aerooffers-cosmosdb" \
    --resource-group $RESOURCE_GROUP \
    --enable-free-tier true \
    --default-consistency-level "Session"

# create backend container app
az containerapp create \
    --name aerooffers-api \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --secrets "db-credential=$COSMOSDB_CREDENTIAL" "registry-password=$CONTAINER_REGISTRY_PASSWORD" \
    --registry-server $CONTAINER_REGISTRY_SERVER \
    --registry-username "lwitkowski" \
    --registry-password "secretref:registry-password" \
    --image $CONTAINER_REGISTRY/aerooffers-api:$DOCKER_IMAGE_TAG \
    --env-vars "COSMOSDB_URL=$COSMOSDB_URL" "COSMOSDB_DB_NAME=$COSMOSDB_DB_NAME" "COSMOSDB_CREDENTIAL=secretref:db-credential" \
    --target-port 80 \
    --ingress external \
    --query properties.configuration.ingress.fqdn \
    --cpu 0.25 --memory 0.5Gi \
    --min-replicas 1 --max-replicas 1

# create scheduled jobs
az containerapp job create \
    --name update-fx-job \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --trigger-type "Schedule" \
    --cron-expression "15 8,16 * * *" \
    --replica-timeout 1800 \
    --secrets "db-credential=$COSMOSDB_CREDENTIAL" "registry-password=$CONTAINER_REGISTRY_PASSWORD" \
    --registry-server $CONTAINER_REGISTRY_SERVER \
    --registry-username "lwitkowski" \
    --registry-password "secretref:registry-password" \
    --image $CONTAINER_REGISTRY/aerooffers-api:$DOCKER_IMAGE_TAG \
    --env-vars "COSMOSDB_URL=$COSMOSDB_URL" "COSMOSDB_DB_NAME=$COSMOSDB_DB_NAME" "COSMOSDB_CREDENTIAL=secretref:db-credential" \
    --command "sh" "./run_update_fx_rates.sh" \
    --cpu "0.25" --memory "0.5Gi"

az containerapp job create \
    --name update-offers-job \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --trigger-type "Schedule" \
    --cron-expression "17 3/11 * * *" \
    --replica-timeout 1800 \
    --secrets "db-credential=$COSMOSDB_CREDENTIAL" "registry-password=$CONTAINER_REGISTRY_PASSWORD" \
    --registry-server $CONTAINER_REGISTRY_SERVER \
    --registry-username "lwitkowski" \
    --registry-password "secretref:registry-password" \
    --image $CONTAINER_REGISTRY/aerooffers-api:$DOCKER_IMAGE_TAG \
    --env-vars "COSMOSDB_URL=$COSMOSDB_URL" "COSMOSDB_DB_NAME=$COSMOSDB_DB_NAME" "COSMOSDB_CREDENTIAL=secretref:db-credential" \
    --command "sh" "./run_update_offers.sh" \
    --cpu "1" --memory "2Gi"