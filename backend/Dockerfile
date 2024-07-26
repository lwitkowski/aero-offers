# syntax=docker/dockerfile:1

FROM python:3.9.6

RUN /usr/local/bin/python -m pip install --upgrade pip

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV FLASK_APP=./web/flask_app.py

COPY . .

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]