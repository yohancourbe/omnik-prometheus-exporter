# omnik-prometheus-exporter
A simple exporter for Omnik inverters

# Credit

Most of this code comes from the repository https://github.com/Woutrrr/Omnik-Data-Logger, I just changed it to work with prometheus.

# Build

```
docker build -t omnik-exporter:latest .
```

# Usage

Set the following environment variables to match your settings:

- `INVERTER_IP`: IP address of your Omnik inverter
- `INVERTER_PORT`: Port of your Omnik inverter (default: 8899)
- `INVERTER_WIFI_SN`: S/N of the wifi kit

```
docker run -d \
  --env INVERTER_IP=192.168.1.198 \
  --env INVERTER_PORT=8899 \
  --env INVERTER_WIFI_SN=632165821 \
  --name omnik-exporter \
  omnik-exporter:latest
```

Configure scraping job in Prometheus

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
  --env INVERTER_IP=192.168.1.198 \
  --env INVERTER_PORT=8899 \
  --env INVERTER_WIFI_SN=632165821 \
  --name omnik-exporter \
  --network home-network \
  omnik-exporter:latest
```
