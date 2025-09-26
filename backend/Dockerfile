# syntax=docker/dockerfile:1

FROM python:3.13-alpine

WORKDIR /app

RUN apk add --no-cache --virtual .build-deps python3-dev build-base linux-headers pcre-dev libffi-dev gcc g++

RUN python3 -m pip install uv flask

COPY . .
RUN uv build

EXPOSE 80

CMD [ "python", "-m" , "flask", "--app=./src/api/flask_app.py", "run", "--host=0.0.0.0", "--port=80"]