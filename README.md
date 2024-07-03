# www.aero-offers.com

# Local development
## Prerequisites (one time activity)
- python 3, pip3, flask
- docker (compose)
- npm

```bash
pip3 install -r requirements.txt
```
update settings.py & settings_dev.py

Start local Postgres
```bash
cd db && docker-compose up -d
```

restore some data from backup
```bash
cd db && unzip -c prod_dump_2024_06_31.sql.zip | psql -h localhost -p 25432 -U aircraft_offers -d aircraft_offers
```

Start backend api (python app):
```
python3 ./web/flask_app.py
```

Start frontend (vue app):
```
cd frontend
npm run serve
```

## Deployment
The backend (the API with Python/Flask) runs with uwsgi on an nginx server.

### UWSGI

runs with user uwsgi:nginx 

### systemd
wird verwendet, um UWSGI zu starten (was dann die Python Prozesse startet)
siehe ``/etc/systemd/system/uwsgi.service`` Definition.

