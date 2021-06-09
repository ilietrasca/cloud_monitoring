#! /bin/bash
sudo apt-get update

# Prepare directory structure
cd /home/ubuntu
mkdir prometheus
chmod 777 prometheus

# clone repo
git clone https://github.com/ilietrasca/cloud_monitoring.git >> start-up.log 2>&1

# install docker and docker-compose
sudo /home/ubuntu/cloud_monitoring/scripts/install-docker.sh >> start-up.log 2>&1

# start project
sudo docker-compose -f /home/ubuntu/cloud_monitoring/docker-compose.yml up -d 

# Install grafana worldmap panel
sleep 10
sudo docker exec -i grafana  bash -c "grafana-cli plugins install grafana-worldmap-panel"

# Restart grafana
sudo docker restart grafana
