# Aero-offers

This project aims at reviving [aero-offers.com](aero-offers.com) - invaluable source of price trends for gliders and other aircrafts, originally developed and maintained by @rthaenert

## Development

[![CD - UI](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-ui.yaml/badge.svg)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-ui.yaml) 
[![CD - Backend (api, jobs)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-backend.yaml/badge.svg)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-backend.yaml)

### Project structure (building blocks /  deployment units)

- `ui` - vue.js application. Deployed as Azure Static Web App (for free).
- `backend/api` - python flask app with few REST endpoints. Deployed as Azure Container App (running 24/7) 
- `backend/jobs` - python scripts triggered periodically. Much more resource-heavy than API, bundled in the same Docker image as `api`, deployed as Azure Container Job.
    - `run_update_offers` - scans few portals (e.g. soaring.de) and stores new offers in the database, then assigns manufacturer and model to new (not yet classified) offers stored in the database
- `db` - Azure CosmosDb NoSQL fully managed database (for free; check https://github.com/lwitkowski/aero-offers/pull/135 for decision record).

#### Deployment

Trunk Based Development and Continuous Deployment is utilized here - all changes pushed/merged to main are automatically deployed to production env. Currently, the project is running in Azure, managed via Terraform.

### TODO
- [ ] Scraper: update db offer if price or location (or any other parameter) has changed
- [x] UI: consent banner for GA
- [ ] aero-offers.com
- [ ] Improve aircraft types structure and introduce 2 levels: glider (e.g Discus 2c 18m) and model (Discus 2cFES 18m) as prices between models sometimes differ significantly
- [ ] utilize https://github.com/weglide/GliderList as source of truth for glider types/models
- [ ] UI: admin panel for manual (re) classification (or community-based)
- [ ] crawler for Facebook Marketplace - do they have an api?
- [ ] crawler for https://www.aircraft24.de
- [ ] crawler for https://plane-sale.com
- [ ] Migrate to managed identity for API and update-offers job to Cosmos DB communication

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

Run crawlers/spiders & reclassifier:
```
cd backend
./run_spiders.sh && ./run_classifier.sh
```