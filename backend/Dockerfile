# syntax=docker/dockerfile:1

FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps python3-dev build-base linux-headers pcre-dev libffi-dev gcc g++ postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY . .

EXPOSE 80

ENV PYTHONPATH=$PYTHONPATH':./src'

CMD [ "python3", "-m" , "flask", "--app=./src/api/flask_app.py", "run", "--host=0.0.0.0", "--port=80"]