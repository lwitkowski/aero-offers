RESOURCE_GROUP=rg-aerooffers
LOCATION="Switzerland North"
ENV_NAME=cae-aerooffers-prod
ACR=lwitkowski.azurecr.io
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

docker login $ACR

az containerapp create \
    --name ca-aerooffers-api \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --registry-server $ACR \
    --image $ACR/aerooffers-api:$DOCKER_IMAGE_TAG \
    --env-vars DB_HOST="???" DB_PORT="5432" DB_NAME="???" DB_USER="???" DB_PW="???" \
    --target-port 80 \
    --ingress internal \
    --transport tcp \
    --cpu 0.25 --memory 0.5Gi \
    --min-replicas 1 --max-replicas 1

az containerapp create \
    --name ca-aerooffers-ui \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --registry-server $ACR \
    --image $ACR/aerooffers-ui:$DOCKER_IMAGE_TAG \
    --target-port 80 \
    --cpu 0.25 --memory 0.5Gi \
    --min-replicas 1 --max-replicas 1 \
    --ingress external \
    --query properties.configuration.ingress.fqdn


# create scheduled jobs
az containerapp job create \
    --name aerooffers-update-fx-job \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --trigger-type "Schedule" \
    --cron-expression "15 8,16 * * *" \
    --replica-timeout 1800 \
    --registry-server $ACR \
    --image $ACR/aerooffers-api:$DOCKER_IMAGE_TAG \
    --secrets "db-user=$DB_USER" "db-password=$DB_PASS" \
    --env-vars "DB_HOST=$DB_HOST" "DB_PORT=$DB_PORT" "DB_NAME=$DB_NAME" "DB_USER=secretref:db-user" "DB_PW=secretref:db-password" \
    --command "sh" "./run_update_fx_rates.sh" \
    --cpu "0.25" --memory "0.5Gi"

az containerapp job create \
    --name aerooffers-update-offers-job \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --trigger-type "Schedule" \
    --cron-expression "17 3 * * *" \
    --replica-timeout 1800 \
    --registry-server $ACR \
    --image $ACR/aerooffers-api:$DOCKER_IMAGE_TAG \
    --secrets "db-user=$DB_USER" "db-password=$DB_PASS" \
    --env-vars "DB_HOST=$DB_HOST" "DB_PORT=$DB_PORT" "DB_NAME=$DB_NAME" "DB_USER=secretref:db-user" "DB_PW=secretref:db-password" \
    --command "sh" "./run_update_offers.sh" \
    --cpu "1" --memory "2Gi"