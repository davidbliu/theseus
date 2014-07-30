import requests
import json
import urllib
import yaml
import etcd
data = yaml.load(open('mesos.yaml', 'r'))
port = 5050
host = data['marathon']['host']
etcd_host_address = data['etcd']['host']
r = requests.get('http://'+host+':'+str(port)+'/state.json')
state = json.loads(r.content)
#
# return a list of slave hosts
#
def get_slave_hosts():
	# print 'http://'+host+':'+str(port)+'/state.json'
	
	slaves = state['slaves']
	# print slaves
	# print slaves.keys()
	return map(lambda x: x['hostname'], slaves)
	

#
# returns all running containers
#
def get_running_containers():
	etcd_client = etcd.Client(host=etcd_host_address, port=4001)
#
# returns containers running on this host
#
def get_slave_containers(host):
	# print 'doing this'
	# r = requests.get('http://'+host+':'+str(port)+'/state.json')
	# print 'good'
	state = json.loads(r.content)
	# slaves = state['slaves']
	print state['slaves'][0].keys()
	# return slaves


if __name__ == "__main__":
	slave_hosts = get_slave_hosts()
	# print 'dont thiss'
	# print slave_hosts
	containers = get_slave_containers(slave_hosts[0])
	print containers