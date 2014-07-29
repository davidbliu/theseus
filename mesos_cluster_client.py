import requests
import json
import urllib
import yaml
import etcd
data = yaml.load(open('mesos.yaml', 'r'))
port = 5050
host = data['marathon']['host']
etcd_host_address = data['etcd']['host']

#
# return a list of slave hosts
#
def get_slave_hosts():
	r = requests.get('http://'+host+':'+str(port)+'/state.json')
	state = json.loads(r.content)
	slaves = state['slaves']
	# print slaves.keys()
	print map(lambda x: x['hostname'], slaves)

#
# returns all running containers
#
def get_running_containers():
	etcd_client = etcd.Client(host=etcd_host_address, port=4001)
#
# returns containers running on this host
#
def get_slave_containers(host):
	print 'hji'
get_slave_hosts()