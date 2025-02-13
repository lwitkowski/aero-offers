RESOURCE_GROUP=rg-aerooffers
LOCATION="Switzerland North"
ENV_NAME=cae-aerooffers-prod
CONTAINER_REGISTRY_SERVER=ghcr.io
CONTAINER_REGISTRY=${CONTAINER_REGISTRY_SERVER}/lwitkowski
DOCKER_IMAGE_TAG=e314458
DB_HOST=localhost
DB_PORT=5432
DB_NAME="aerooffers"
DB_USER="aerooffers"
DB_PASS="aerooffers"

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

# create backend container app
az containerapp create \
    --name ca-aerooffers-api \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --registry-server $CONTAINER_REGISTRY_SERVER \
    --image $CONTAINER_REGISTRY/aerooffers-api:$DOCKER_IMAGE_TAG \
    --secrets "db-user=$DB_USER" "db-password=$DB_PASS" \
    --env-vars "DB_HOST=$DB_HOST" "DB_PORT=$DB_PORT" "DB_NAME=$DB_NAME" "DB_USER=secretref:db-user" "DB_PW=secretref:db-password" \
    --target-port 80 \
    --ingress external \
    --query properties.configuration.ingress.fqdn \
    --cpu 0.25 --memory 0.5Gi \
    --min-replicas 1 --max-replicas 1

# create scheduled jobs
az containerapp job create \
    --name aerooffers-update-fx-job \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --trigger-type "Schedule" \
    --cron-expression "15 8,16 * * *" \
    --replica-timeout 1800 \
    --registry-server $CONTAINER_REGISTRY_SERVER \
    --image $CONTAINER_REGISTRY/aerooffers-api:$DOCKER_IMAGE_TAG \
    --secrets "db-user=$DB_USER" "db-password=$DB_PASS" \
    --env-vars "DB_HOST=$DB_HOST" "DB_PORT=$DB_PORT" "DB_NAME=$DB_NAME" "DB_USER=secretref:db-user" "DB_PW=secretref:db-password" \
    --command "sh" "./run_update_fx_rates.sh" \
    --cpu "0.25" --memory "0.5Gi"

az containerapp job create \
    --name aerooffers-update-offers-job \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --trigger-type "Schedule" \
    --cron-expression "17 3/11 * * *" \
    --replica-timeout 1800 \
    --registry-server $CONTAINER_REGISTRY_SERVER \
    --image $CONTAINER_REGISTRY/aerooffers-api:$DOCKER_IMAGE_TAG \
    --secrets "db-user=$DB_USER" "db-password=$DB_PASS" \
    --env-vars "DB_HOST=$DB_HOST" "DB_PORT=$DB_PORT" "DB_NAME=$DB_NAME" "DB_USER=secretref:db-user" "DB_PW=secretref:db-password" \
    --command "sh" "./run_update_offers.sh" \
    --cpu "1" --memory "2Gi"