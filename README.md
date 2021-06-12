# Cloud Monitoring Project

## Personal project, monitor SLA breach in cloud.

## Architecture overview from AWS
![](https://github.com/ilietrasca/cloud_monitoring/blob/master/CloudMonitoring.png)

### Install dependencies to test on local
1. In the working directory run below commands to install the dependencies:
```
$ pip-compile requirments.in
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

### Deploy AWS 
2. Supposed that you have already configured AWS credentials and you have required permissions
```
$ date; aws cloudformation create-stack --stack-name CloudMonitoringAWS --template-body file://cloudforamtion/cloud-monitoring.yaml --capabilities CAPABILITY_NAMED_IAM 
```
