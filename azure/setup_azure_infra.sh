RESOURCE_GROUP=rg-aerooffers
LOCATION="Switzerland North"
ENV_NAME=cae-aerooffers-prod
ACR=lwitkowski.azurecr.io

az group create \
  --name $RESOURCE_GROUP \
  --location "$LOCATION"

az containerapp env create \
  --name $ENV_NAME \
  --resource-group $RESOURCE_GROUP \
  --location "$LOCATION"

docker login $ACR

az containerapp create \
    --name ca-aerooffers-db \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --registry-server $ACR \
    --image $ACR/aerooffers-db:1 \
    --env-vars POSTGRES_DB="aircraft_offers" POSTGRES_USER="aircraft_offers" POSTGRES_PASSWORD="aircraft_offers" \
    --target-port 5432 \
    --ingress internal \
    --transport tcp \
    --cpu 0.25 --memory 0.5Gi \
    --min-replicas 0 --max-replicas 1

az containerapp create \
    --name ca-aerooffers-api \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --registry-server $ACR \
    --image $ACR/aerooffers-api:a7e18a5 \
    --env-vars DB_HOST="ca-aerooffers-db" DB_PORT="5432" DB_NAME="aircraft_offers" DB_USER="aircraft_offers" DB_PW="aircraft_offers" \
    --target-port 80 \
    --ingress internal \
    --cpu 0.25 --memory 0.5Gi \
    --min-replicas 0 --max-replicas 1

az containerapp create \
    --name ca-aerooffers-ui \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --registry-server $ACR \
    --image $ACR/aerooffers-ui:a7e18a5 \
    --target-port 80 \
    --cpu 0.25 --memory 0.5Gi \
    --min-replicas 0 --max-replicas 1 \
    --ingress external \
    --query properties.configuration.ingress.fqdn

