#!/usr/bin/env python3
# Cloud Monitoring
# Author: Laurentiu Trasca

try:
    import random
    import time
    import os
    import logging
    import sys
    import requests
    import unittest
    import json
    import re
    from var import geohashMap, rds
    from bs4 import BeautifulSoup
    from prometheus_client import start_http_server
    from prometheus_client.openmetrics.exposition import generate_latest
    from prometheus_client import Counter, Summary, Gauge, Histogram, Enum
except ImportError:
    print("could not load needed modules, exiting_transaction...")
    exit(1)


__version__ = "0.1"

metrics_port= os.environ.get("METRICS_PORT", 8001)

logging.basicConfig(level = "INFO", datefmt = "%Y-%m-%d %H:%M:%S %z", format = "[%(asctime)s] [%(levelname)s] %(message)s")
logging.info("Starting program version {0}".format(__version__))
logging.info("Using log level {0}".format("INFO"))


# start the http server to expose the prometheus metrics
logging.info("Starting web-server...")
start_http_server(metrics_port, "0.0.0.0")
logging.info("Server started and listening at 0.0.0.0:{0}".format(metrics_port))


def check_status_aws():

    aws_region_services_health =  Gauge('aws_region_health', 'Service status for AWS Cloud at Region level',['service','country','geohash','category'])
    aws_global_services_health =  Gauge('aws_health', 'Service status for AWS Cloud global',['service'])
    while True:
        URL = 'https://status.aws.amazon.com/'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        #results = soup.find(id='main_table_countries')
        #fix after upgrade
        results = soup.find(id='statusHistory statusHistoryContent')

        for row in soup.select('tbody tr'):
            row_text = [x.text for x in row.find_all('td')]
            # service_name = str(row_text[1]).strip("(")
            country_in_map = re.findall(r'\(.*?\)', str(row_text[1]))
            if country_in_map:
                country_in_map = country_in_map[0].strip("()")
                service_name = re.search('(.+?)\(', str(row_text[1])).group(1)
                service_category = "Database" if service_name in rds else "AWS Service"
            else:
                aws_global_services_health.labels(service = str(row_text[1])).set(1)
                continue
            if country_in_map in geohashMap.keys():
                location = geohashMap[country_in_map]
            else: continue
            
            if str(row_text[2]) == "Service is operating normally":
                aws_region_services_health.labels(service = service_name, country = country_in_map, geohash = location, category = service_category).set(1)
            else:
                aws_region_services_health.labels(service = service_name, country = country_in_map, geohash = location).set(0)
        time.sleep(10)

if __name__ == '__main__':
    check_status_aws()