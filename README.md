# Aero-offers

This project aims at reviving [aero-offers.com](aero-offers.com) - invaluable source of price trends for gliders and other aircrafts, originally developed and maintained by @rthaenert

## Development

[![CD - UI](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-ui.yaml/badge.svg)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-ui.yaml) 
[![CD - Backend (api, jobs)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-backend.yaml/badge.svg)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-backend.yaml)

### Project structure (building blocks /  deployment units)

- `ui` - vue.js application. Deployed as Azure Static Web App (for free).
- `backend`
  - web api:
    - python flask app with few REST endpoints
    - deployed as a lightweight Azure Container App (running 24/7) 
  - update offers scheduled job:
    - scrapes new offers from few ads portals (e.g. soaring.de) and stores them in the database
    - runs classifier for not yet classified offers to find exact manufacturer and model, utilizing Gemini LLM api, which provides excellent accuracy compared to legacy, rule-based classifier.
    - it's much more resource-heavy than API, bundled in the same Docker image as `api`, deployed as Azure Container Job.
    
- `db` - Azure CosmosDb NoSQL fully managed database (for free; check https://github.com/lwitkowski/aero-offers/pull/135 for decision record).
- `terraform` - deployment infrastructure to Azure

#### Infrastructure

Azure resources are split into two resource groups:
- `rg-aerooffers-platform` - long-lived platform resources **not managed by Terraform**: TF state storage, GitHub Actions managed identity. Created once via `terraform/setup-azure-bootstrap.sh`.
- `rg-aerooffers` - application resources managed by Terraform: Container Apps, CosmosDB, Storage, Log Analytics, alerting.

First-time setup: run `terraform/setup-azure-bootstrap.sh`, then configure the GitHub secrets it outputs.

#### Deployment

Trunk Based Development and Continuous Deployment is utilized here - all changes pushed/merged to main are automatically deployed to production env. Currently, the project is running in Azure, managed via Terraform.

### TODO
- [ ] Scraper: update db offer if price or location (or any other parameter) has changed
- [ ] aero-offers.com
- [ ] improve aircraft types structure and introduce 2 levels: glider (e.g Discus 2c 18m) and model (Discus 2cFES 18m) as prices between models sometimes differ significantly
- [ ] admin panel for manual (re) classification (or community-based)
- [ ] crawler for Facebook Marketplace - do they have an api?
- [ ] crawler for https://www.aircraft24.de
- [ ] crawler for https://plane-sale.com

### Running backend locally without Python
`docker compose up --build` - starts CosmosDb and Python Flask backend

### Prerequisites for local development with hot reloads
- python 3.13+
- uv (`pip install uv`)
- docker (compose)
- nodejs

Start CosmosDb emulator in docker (available for debugging via `localhost:1234`):
```bash
docker-compose up cosmosdb
```

Init python environment
```bash
cd backend
uv sync
```

Set up auto-formatting and lint fix before commit (recommended:
```bash
git config core.hooksPath hooks
```

Start backend api (python app):
```
cd backend
./run_api_in_docker.sh
```

Start UI (vue app):
```
cd ui
npm run dev
```
UI has own, detailed README.md file.

Run crawlers/spiders & classifier:
```
cd backend
./run_spiders.sh && ./run_classifier.sh
```