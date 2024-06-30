# www.aero-offers.com

## lokale Entwicklung

Backend starten mit 

```/usr/local/bin/python3.7 /Users/ralf/Desktop/AircraftOffers/web/flask_app.py```

Frontend starten mit
 
````npm run serve````

## Deployment

Das Backend (die API mit Python/Flask) läuft mit uwsgi auf einem nginx Server.

### UWSGI

läuft mit User uwsgi:nginx 

### systemd
wird verwendet, um UWSGI zu starten (was dann die Python Prozesse startet)
siehe ``/etc/systemd/system/uwsgi.service`` Definition.

