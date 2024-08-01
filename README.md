# Aero-offers

This project aims at reviving [aero-offers.com](aero-offers.com) - invaluable source of price trends for gliders and other aircrafts, originally developed and maintained by @rthaenert

## Development

[![CD - UI](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-ui.yaml/badge.svg)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-ui.yaml) 
[![CD - Backend (api, jobs)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-backend.yaml/badge.svg)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd-backend.yaml)

### Project structure (building blocks /  deployment units)
- `ui` - vue.js application deployed as dockerized static web app served by nginx
- `backend/api` - python flask app with few REST endpoints, reversed proxied by nginx serving frontend (not exposed directly to the internet). 
- `backend/jobs` - python scripts triggered by scheduled job (e.g once a day). Please mind those jobs may be much much more resource heavy than API, and should not be triggered from within `api` container which is optimised to handle REST api traffic.
    - `job_fetch_offers` - scans few portals (e.g. soaring.de) and stores new offers in the database (not yet classified)
    - `job_reclassify_offers` - assigns manufacturer and model to new (not yet classified) offers stored in the database
    - `job_update_exchange_rates` - updates currency exchange rates based ok ECP api
- `db` - PostgreSQL 16 database with DDL scripts managed by Flyway. Currently running inside cheapest possible Azure VM.

### Prod environment
Currently, the project is being onboarded to Azure Cloud (still WIP).

### TODO
- [x] deploy working ui, api and db to Azure
- [x] fix segelflug spider/crawler
- [x] good enough DB setup (cheap VM)
- [x] use Azure secrets for db credentials
- [x] setup cron triggers for crawlers, reclassifier and FX rates updater
- [x] human readable domain (aero-offers.pl)
- [x] fix aircraft type dropdown
- [ ] infra as code (biceps or terraform)
- [ ] document infra and env topology
- [ ] fix other spiders/crawlers
- [ ] redirect from aero-offers.com
- [ ] fix & polish CSS in UI
- [ ] update/simplify legal subpage
- [ ] cookies info
- [ ] use https://github.com/weglide/GliderList  
- [ ] admin panel for manual (re) classification (or community-based)
- [ ] crawler for Facebook Marketplace - do they have nice api?
- [ ] crawler for https://www.aircraft24.de
- [ ] crawler for http://www.airplanemart.com
- [ ] crawler for http://www.aeronave.de/1-luftfahrzeuge/listings.html
- [ ] crawler for https://plane-sale.com

### Running locally without Python nor NodeJS
`docker compose up --build` - starts postgres, python backend and UI apps (http://localhost:8080/)

### Prerequisites for local development with hot reloads
- python 3.12+, pip3, flask
- docker (compose)
- npm

Start Postgres in docker (available for debugging via `localhost:25432`):
```bash
docker-compose up postgres flyway
```

Unzip database backup (optional) and load into DB
```bash
cd db && unzip -qq prod_dump_2024_06_31.sql.zip
```

Install python packages
```bash
cd backend
pip3 install -r requirements.txt -r tests/requirements.txt 
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