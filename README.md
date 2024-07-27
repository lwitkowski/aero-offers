# Aero-offers

This project aims at reviving www.aero-offers.com - invaluable source of price trends for gliders and other aircrafts.

## Development

[![Continuous Deployment](https://github.com/lwitkowski/aero-offers/actions/workflows/cd.yaml/badge.svg)](https://github.com/lwitkowski/aero-offers/actions/workflows/cd.yaml)

### Project structure
There are 3 building blocks / modules / deployment units:
- `frontend` - vue.js application deployed as dockerized static web app served by nginx
- `backend` - python flask app with few REST endpoints, reversed proxied by nginx serving frontend (not exposed directly to the internet). Spiders/crawlers that scrape different portals reside here as well.
- `db` - PostgreSQL 15 database

### TODO
- use Azure secrets for db credentials
- managed db with persistent storage (now it's running in ephemeral container)
- fix spiders/crawlers and setup cron triggers (Azure Functions?)
- infra as code (biceps or terraform)
- document infra and env topology
- human readable domain (aero-offers.com?)
- fix aircraft type dropdown
- update/simplify legal subpage

### Running locally without Python nor NodeJS
`docker compose up --build` - starts postgres, python backend and frontend apps (http://localhost:8080/)

### Prerequisites for local development with hot reloads
- python 3.12+, pip3, flask
- docker (compose)
- npm

Unzip database backup (optional)
```bash
cd db && unzip -qq prod_dump_2024_06_31.sql.zip
```

Start postgres in docker (exposed on port 25432):
```bash
docker-compose up postgres
```

Install python packages
```bash
pip3 install -r requirements.txt
```

Start backend api (python app):
```
cd backend
python3 ./web/flask_app.py
```

Start frontend (vue app):
```
cd frontend
npm run serve
```

## Further development / bug fixing (from Ralf)

- Model information
- Scale axes correctly (!)
- Euro on y-axis
- Top 10 aircraft offered per category
- Add more spiders
- https://www.aircraft24.de
- http://www.airplanemart.com
- http://www.aeronave.de/1-luftfahrzeuge/listings.html
- https://plane-sale.com

### Legal (from Ralf)
- Opt-out option / banner, pop-up due to analytics cookies
- Imprint generator: https://www.e-recht24.de/impressum-generator.html
- Data protection declaration generator: https://datenschutz-generator.de

Imprint and data protection declaration must be listed separately, but may refer to the same page (if desired).
