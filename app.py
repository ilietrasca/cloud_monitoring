#!/usr/bin/env python3
# CloudMonitoring
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
    from bs4 import BeautifulSoup
    from prometheus_client import start_http_server
    from prometheus_client.openmetrics.exposition import generate_latest
    from prometheus_client import Counter, Summary, Gauge, Histogram, Enum
except ImportError:
    print("could not load needed modules, exiting_transaction...")
    exit(1)


__version__ = "0.1"

metrics_port= os.environ.get("METRICS_PORT", 8001)

log_levels = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20, "DEBUG": 10, "NOTSET": 0}
log_level_name = os.environ.get("LOG_LEVEL", "INFO")
log_level = log_levels[log_level_name]
log_fmt = "[%(asctime)s] [%(levelname)s] %(message)s"

logging.basicConfig(level = log_level, datefmt = "%Y-%m-%d %H:%M:%S %z", format = log_fmt)
logging.info("Starting program version {0}".format(__version__))
logging.info("Using log level {0}".format(log_level_name))


# start the http server to expose the prometheus metrics
logging.info("Starting web-server...")
start_http_server(metrics_port, "0.0.0.0")
logging.info("Server started and listening at 0.0.0.0:{0}".format(metrics_port))

global geohashMap
geohashMap =  {"China": "wq1","Italy": "sr8r","SKorea": "wyd","Iran": "tjw","France": "u03d","Germany": "u1p","DiamondPrincess": "we","Spain": "ezj","Japan": "xn6","USA": "9z0","Switzerland": "u0md","UK": "gcqv","Netherlands": "u15z","Sweden": "u75","Belgium": "u0gq","Norway": "u4y","Singapore": "w21ze","HongKong": "wecpn","Austria": "u26q","Malaysia": "w28","Bahrain": "thegy","Australia": "qgx","Greece": "sqzv","Canada": "cdp","Kuwait": "tj1y","Iraq": "svye","Iceland": "ge7p","Thailand": "w4xt","Egypt": "sst","Taiwan": "wsnn","UAE": "thn","India": "tg8","SanMarino": "srbcgx","Denmark": "u1z5","Lebanon": "sy19","Czechia": "u2fd","Portugal": "eyfn","Vietnam": "w6m","Israel": "sv2z","Finland": "ue42","Ireland": "gc6","Algeria": "shc","Brazil": "6y","Palestine": "sv9h","Russia": "y51","Oman": "t78","Slovenia": "u24q","Qatar": "thkr","Romania": "u81","Ecuador": "6r8p","Georgia": "szqa","Croatia": "u24b","SaudiArabia": "th3","Philippines": "wdp","Macao": "webwp","Estonia": "ud6q","Argentina": "699x","Azerbaijan": "tp4","Chile": "67nn","Poland": "u3mb","Mexico": "9sp","Pakistan": "tt3","Hungary": "u2mg","Belarus": "u9kp","Indonesia": "qxny","Peru": "6q4","DominicanRepublic": "d7mg","Luxembourg": "u0u6","NewZealand": "rb6","CostaRica": "d1u0","FrenchGuiana": "dbf3","Slovakia": "u2ts","Afghanistan": "tmy","Senegal": "edt","Bulgaria": "sx9c","Latvia": "ud4e","NorthMacedonia": "srrk","Bangladesh": "wh0r","BosniaandHerzegovina": "srug","Malta": "sq6k0","SouthAfrica": "kd9","Cambodia": "w66","Morocco": "eve","Cameroon": "s2c","FaeroeIslands": "gg51","Maldives": "mxuh0","Andorra": "sp94h","Armenia": "szpu","Jordan": "sdv1","Lithuania": "u9c4","Monaco": "spub","Nepal": "tv5b","Nigeria": "s5n","SriLanka": "tc3","Tunisia": "snnb","Ukraine": "u8w","Bhutan": "whb7","Colombia": "d2e","Gibraltar": "eykj","VaticanCity": "sr2y7k","Liechtenstein": "u0qu1","Moldova": "u8kk","Paraguay": "6ey","Serbia": "sryc","Togo": "s12z","Albania": "srq4","SaintMartin": "de5nt","StBarth": "de5mf6","Guyana": "d8y","Martinique": "ddse","Turkey":"syb"}

def check_status_aws():

    aws_region_services_health =  Gauge('aws_region_health', 'Service status for AWS Cloud at Region level',['service','country','geohash'])
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
            else:
                aws_global_services_health.labels(service = str(row_text[1])).set(1)
                continue
            if country_in_map in geohashMap.keys():
                location = geohashMap[country_in_map]
            else: continue
            
            if str(row_text[2]) == "Service is operating normally":
                aws_region_services_health.labels(service = service_name, country = country_in_map, geohash = location).set(1)
            else:
                aws_region_services_health.labels(service = service_name, country = country_in_map, geohash = location).set(0)
        time.sleep(10)

if __name__ == '__main__':
    check_status_aws()