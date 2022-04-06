FROM ubuntu

RUN apt-get update \
  && apt-get install -y locales \
  && apt-get install -y python \
  && rm -rf /var/lib/apt/lists/* \
  && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

ENV LANG en_US.utf8

RUN useradd -ms /bin/bash app

USER app

WORKDIR /home/app

ADD ./app/ /home/app

EXPOSE 8080

CMD ["python", "./PrometheusExporterWebserver.py"]