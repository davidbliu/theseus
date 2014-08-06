import yaml
from marathon import MarathonClient
import sys
import yaml
# import Entities as entities
import os
# data = yaml.load(open('mesos.yaml', 'r'))
# etcd_host = data['etcd']['host']
# marathon_host = data['marathon']['host']
# marathon_port = data['marathon']['port']

def update_group(service_name, encoded_labels, config, existing_marathon_apps, delta = 0):
	custom_constraints = group.config.get('custom_constraints')
	if custom_constraints:
		print 'cant do custom constraints yet sorry'
	else:
		app_id = existing_marathon_apps[0]
		instances = config.get('instances')
		if not instances:
			instances = 1+delta
		else:
			instances = int(instances)+delta
		config['instances'] = instances
		update_app(app_id, config, instances)
#
# update an app in marathon
#
def update_app(app_id, config, instances = 1):
	#
	# set up marathon client and launch container
	#
	image_string = 'docker:///' + config['image']
	marathon_client = MarathonClient('http://' + str(data['marathon']['host']) + ':' + str(data['marathon']['port']))
	app = marathon_client.get_app(app_id)
	#
	# set up options for cassandra TODO this is terrible dawg
	#
	decoded = entities.decode_marathon_id(app_id)
	options = []
	if str(decoded['service']) == "cassandra":
		options = ["-p", "7000:7000", "-p", "9042:9042", "-p", "9160:9160", "-p", "22000:22", "-p", "5000:5000"]
		# ports = []
		# constraints = [["hostname", "UNIQUE"]]
	
	marathon_client.update_app(
		app_id,
		app,
		instances = instances,
		container = {
			"image" : image_string, 
			"options" : options
		}
	)

