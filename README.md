# omnik-prometheus-exporter
A simple exporter for Omnik inverters

# Credit

Most of this code comes from the repository https://github.com/Woutrrr/Omnik-Data-Logger, I just changed it to work with prometheus.

# Build

```
docker build -t omnik-exporter:latest .
```

# Usage

Edit config-org.conf to match your settings.

```
docker run -d \
  --volume ${PWD}/config-org.cfg:/home/app/config.cfg \
  --name omnik-exporter \
  omnik-exporter:latest
```
