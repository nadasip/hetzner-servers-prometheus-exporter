from prometheus_client import start_http_server, Summary, Gauge, Info
import datetime, time
import requests
import json
import os
import sys

try:
  loadBalancerId = os.environ['LOAD_BALANCER_ID']
except KeyError:
  print('Variable LOAD_BALANCER_ID not defined')
  sys.exit(1)

try:
  accessToken = os.environ['ACCEESS_TOKEN']
except KeyError:
  print('Variable ACCEESS_TOKEN not defined')
  sys.exit(1)

requestUrl = 'https://api.hetzner.cloud/v1/servers/' + loadBalancerId

def getLoadBalancerType(id):
    url = requestUrl
    
    headers = {
        'Content-type': "application/json",
        'Authorization': "Bearer " +  accessToken
    }

    get = requests.get(url, headers=headers)
    return get.json()


def getMetrics(metricsType):
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    hetznerDate = datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

    url = requestUrl + '/metrics'

    headers = {
        'Content-type': "application/json",
        'Authorization': "Bearer " +  accessToken
    }

    data = {
        "type": metricsType,
        "start": hetznerDate,
        "end": hetznerDate,
        "step": 60
    }

    get = requests.get(url, headers=headers, data=json.dumps(data))
    return get.json()


if __name__ == '__main__':

  loadBalancerName = getLoadBalancerType(loadBalancerId)['server']['name']


  
  HetznerServerInfo = Info('hetzner_server', 'Hetzner Server Exporter build info', ['hetzner_vserver_id', 'hetzner_vserver_name'])
  HetznerCpuLoad = Gauge('hetzner_server_cpu_load', 'CPU Load on Hetzner Server', ['hetzner_vserver_id', 'hetzner_vserver_name'])
  HetznerDiskIOpsRead = Gauge('hetzner_server_disk_iops_read', 'Disk IO read operation per second on Hetzner Server', ['hetzner_vserver_id', 'hetzner_vserver_name'])
  HetznerDiskIOpsWrite = Gauge('hetzner_server_disk_iops_write', 'Disk IO write operation per second on Hetzner Server', ['hetzner_vserver_id', 'hetzner_vserver_name'])
  HetznerDiskBandwidthRead = Gauge('hetzner_server_disk_bandwidth_read', 'Disk Bandwidth read operation on Hetzner Server', ['hetzner_vserver_id', 'hetzner_vserver_name'])
  HetznerDiskBandwidthWrite = Gauge('hetzner_server_disk_bandwidth_write', 'Disk Bandwidth write operation on Hetzner Server', ['hetzner_vserver_id', 'hetzner_vserver_name'])
  HetznerNetworkPpsIn = Gauge('hetzner_server_net_packet_per_second_read', 'Network packets per second RX on Hetzner Server', ['hetzner_vserver_id', 'hetzner_vserver_name'])
  HetznerNetworkPpsOut = Gauge('hetzner_server_net_packet_per_second_write', 'Network packets per second TX on Hetzner Server', ['hetzner_vserver_id', 'hetzner_vserver_name'])
  HetznerNetworkBandwidthIn = Gauge('hetzner_server_net_bandwidth_in', 'Nqetwork Bandwidth IN on Hetzner Server', ['hetzner_vserver_id', 'hetzner_vserver_name'])
  HetznerNetworkBandwidthOut = Gauge('hetzner_server_net_bandwidth_out', 'Network Bandwidth OUT on Hetzner Server', ['hetzner_vserver_id', 'hetzner_vserver_name'])
  
  start_http_server(8800)
  print('Web server started on port 8800')

  while True:
    HetznerServerInfo.labels(hetzner_vserver_id=loadBalancerId, hetzner_vserver_name=loadBalancerName).info({'version': '0.0.1', 'buildhost': 'drake0103@gmail.com'})
    HetznerCpuLoad.labels(hetzner_vserver_id=loadBalancerId, hetzner_vserver_name=loadBalancerName).set_function(lambda: getMetrics('cpu')["metrics"]["time_series"]["cpu"]["values"][0][1])
    HetznerDiskIOpsRead.labels(hetzner_vserver_id=loadBalancerId, hetzner_vserver_name=loadBalancerName).set_function(lambda: getMetrics('disk')["metrics"]["time_series"]["disk.0.iops.read"]["values"][0][1])
    HetznerDiskIOpsWrite.labels(hetzner_vserver_id=loadBalancerId, hetzner_vserver_name=loadBalancerName).set_function(lambda: getMetrics('disk')["metrics"]["time_series"]["disk.0.iops.write"]["values"][0][1])
    HetznerDiskBandwidthRead.labels(hetzner_vserver_id=loadBalancerId, hetzner_vserver_name=loadBalancerName).set_function(lambda: getMetrics('disk')["metrics"]["time_series"]["disk.0.bandwidth.read"]["values"][0][1])
    HetznerDiskBandwidthWrite.labels(hetzner_vserver_id=loadBalancerId, hetzner_vserver_name=loadBalancerName).set_function(lambda: getMetrics('disk')["metrics"]["time_series"]["disk.0.bandwidth.write"]["values"][0][1])
    HetznerNetworkPpsIn.labels(hetzner_vserver_id=loadBalancerId, hetzner_vserver_name=loadBalancerName).set_function(lambda: getMetrics('network')["metrics"]["time_series"]["network.0.pps.in"]["values"][0][1])
    HetznerNetworkPpsOut.labels(hetzner_vserver_id=loadBalancerId, hetzner_vserver_name=loadBalancerName).set_function(lambda: getMetrics('network')["metrics"]["time_series"]["network.0.pps.out"]["values"][0][1])
    HetznerNetworkBandwidthIn.labels(hetzner_vserver_id=loadBalancerId, hetzner_vserver_name=loadBalancerName).set_function(lambda: getMetrics('network')["metrics"]["time_series"]["network.0.bandwidth.in"]["values"][0][1])
    HetznerNetworkBandwidthOut.labels(hetzner_vserver_id=loadBalancerId, hetzner_vserver_name=loadBalancerName).set_function(lambda: getMetrics('network')["metrics"]["time_series"]["network.0.bandwidth.out"]["values"][0][1])
    time.sleep(1)

