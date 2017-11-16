
# DC/OS Marathon Scraper

This scraper does a specific thing, that this is.

- Turn /marathon/metrics into prometheus Gauge and Count metrics


##  How to use

```
docker run -d \
  -e PORT0=3456 \
  -e MARATHON_SVC_U=<user> \
  -e MARATHON_SVC_P=<pass> \
  -e DCOS_URL=https://my.dcos.com \
  -p 9091:3456 \
  wallnerryan/marathonscraper:0.0.2

curl http://localhost:9091/metrics
```

## Marathon

Assuming you have the following setup

 - service user username
 - service user password in DC/OS Secrets

