FROM alpine:latest

ENV FLASK_DEBUG "False"

ENV DOMAIN ""

ENV CLIENT_ID ""

ENV CLIENT_SECRET ""

ENV AUDIENCE ""

ENV MANAGEMENT_AUDIENCE ""

ENV CONNECTION ""

MAINTAINER "Rene Cunningham <rene@rene.bz>"

WORKDIR /app

RUN apk upgrade --update-cache --available && apk add python3 \
    python3-dev gcc musl-dev openssl-dev libffi-dev

COPY . .

RUN pip3 install -r requirements.txt

CMD FLASK_APP=app.py flask run --host=0.0.0.0

EXPOSE 5000
