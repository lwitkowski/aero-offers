# Aero-offers

This project aims at reviving [aero-offers.com](aero-offers.com) - invaluable source of price trends for gliders and other aircrafts, originally developed and maintained by @rthaenert

## Development

[![CD - UI](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-ui.yaml/badge.svg)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-ui.yaml) 
[![CD - Backend (api, jobs)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-backend.yaml/badge.svg)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-backend.yaml)

### Project structure (building blocks /  deployment units)

- `ui` - vue.js application. Deployed as Azure Static Web App.
- `backend/api` - python flask app with few REST endpoints, reversed proxied by nginx serving frontend (not exposed directly to the internet). Deployed as Azure Container App (running 24/7) 
- `backend/jobs` - python scripts triggered periodically. Much more resource-heavy than API, bundled in the same Docker image as `api`, deployed as Azure Container Job (with overridden command)
    - `run_update_offers` - scans few portals (e.g. soaring.de) and stores new offers in the database, then assigns manufacturer and model to new (not yet classified) offers stored in the database
    - `run_update_fx_rates` - updates currency exchange rates from ECB REST api
- `db` - Azure CosmosDb NoSQL fully managed database (check https://github.com/lwitkowski/aero-offers/pull/135 for decision record).

#### Deployment

Trunk Based Development and Continuous Deployment is utilized here - all changes pushed/merged to main are automatically deployed to production env. Currently, the project is running in Azure.

### TODO
- [ ] Scraper: update db offer if price or location (or any other parameter) has changed
- [ ] Dev: end 2 end tests of crawlers
- [ ] UI: consent banner for GA
- [x] Infra: db daily backups
- [ ] Infra: infra as code (biceps or terraform)
- [ ] document infra and env topology
- [x] Backend: fix and enable other spiders/crawlers
- [ ] UI: aero-offers.com
- [ ] Improve aircraft types structure and introduce 2 levels: glider (e.g Discus 2c 18m) and model (Discus 2cFES 18m) as prices between models sometimes differ significantly
- [ ] UI: fix & polish CSS in UI
- [ ] utilize https://github.com/weglide/GliderList as source of truth for glider types/models
- [ ] UI: admin panel for manual (re) classification (or community-based)
- [ ] crawler for Facebook Marketplace - do they have nice api?
- [ ] crawler for https://www.aircraft24.de
- [ ] crawler for http://www.airplanemart.com
- [ ] crawler for http://www.aeronave.de/1-luftfahrzeuge/listings.html
- [ ] crawler for https://plane-sale.com

### Running locally without Python nor NodeJS
`docker compose up --build` - starts CosmosDb, python backend and UI apps (http://localhost:8080/)

### Prerequisites for local development with hot reloads
- python 3.12+, pip3, flask
- docker (compose)
- npm

Start CosmosDb emulator in docker (available for debugging via `localhost:1234`):
```bash
docker-compose up cosmosdb
```

Init python environment
```bash
cd backend
./init_dev_env.sh
```

Start backend api (python app):
```
cd backend
./start_api.sh
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