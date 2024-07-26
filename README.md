# www.aero-offers.com

# Running locally
`docker compose up --build` - starts postgres, python backend and frontend apps (http://localhost:8080/)

# Local development

## Prerequisites
- python 3, pip3, flask
- docker (compose)
- npm

```bash
pip3 install -r requirements.txt
```

Prepare database backup (this is optional)
```bash
cd db && unzip -qq prod_dump_2024_06_31.sql.zip
```

Start postgres in docker (exposed on port 25432):
```bash
docker-compose up postgres
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

## Deployment (AWS EC2 setup)
The backend (the API with Python/Flask) runs with uwsgi on an nginx server.

### UWSGI

runs with user uwsgi:nginx 

### systemd
wird verwendet, um UWSGI zu starten (was dann die Python Prozesse startet)
siehe ``/etc/systemd/system/uwsgi.service`` Definition.

Further development / bug fixing
=
- Model information
- Scale axes correctly (!)
- Euro on y-axis
- Top 10 aircraft offered per category
- Add more spiders
- https://www.aircraft24.de
- http://www.airplanemart.com
- http://www.aeronave.de/1-luftfahrzeuge/listings.html
- https://plane-sale.com

Legal
=
- Opt-out option / banner, pop-up due to analytics cookies
- Imprint generator: https://www.e-recht24.de/impressum-generator.html
- Data protection declaration generator: https://datenschutz-generator.de

Imprint and data protection declaration must be listed separately, but may refer to the same page (if desired).
