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

Configure scaping job in Prometheus

```
- job_name: omnik
  honor_timestamps: true
  scrape_interval: 15s
  scrape_timeout: 10s
  metrics_path: /metrics
  scheme: http
  follow_redirects: true
  static_configs:
  - targets:
    - omnik-exporter:8080
```

NB: in order to DNS to work, both prometheus and omnik-exporter must be on the same user-defined network.

```
docker network create home-monitoring
```

And your container must be created with the network specified

```
docker run -d \
  --volume ${PWD}/config-org.cfg:/home/app/config.cfg \
  --name omnik-exporter \
  --network home-network \
  omnik-exporter:latest
```