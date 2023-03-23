# syntax=docker/dockerfile:1

FROM python:3.11-alpine

RUN mkdir /app
WORKDIR /app
COPY . /app

RUN apk update
RUN apk add mongodb-tools
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install -r requirements.txt

EXPOSE 5000
EXPOSE 27017
EXPOSE 27018