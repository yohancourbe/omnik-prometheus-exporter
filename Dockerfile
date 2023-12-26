FROM python:3.12-slim

WORKDIR /usr/src/app

ADD ./app/ /usr/src/app

EXPOSE 8080

CMD ["python", "./PrometheusExporterWebserver.py"]
