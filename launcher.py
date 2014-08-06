import yaml
from marathon import MarathonClient
import requests
import json
import uuid
import ast
import namespacer, etcd_driver
import os
marathon_host = os.environ['MARATHON_HOST']
marathon_port = os.environ['MARATHON_PORT']
etcd_host = os.environ['ETCD_HOST_ADDRESS']
# data = yaml.load(open('mesos.yaml', 'r'))
# etcd_host = data['etcd']['host']
# marathon_host = data['marathon']['host']
# marathon_port = data['marathon']['port']


#
# launches a single app. you may need to launch several apps for fixed host groups
#
def launch_app(service_name, app_id, config, labels = [], instances = -1):
	print 'launching ' + service_name
	print config #DEBUG
	service_dict = config
	image = service_dict['image']
	try:
		ports = service_dict['ports'].values()
	except:
		ports = []
	if instances == -1:
		instances = 1 if not service_dict.get('instances') else service_dict.get('instances')
	cpus = 0.3 if not service_dict.get('cpus') else service_dict.get('cpus')
	mem = 512 if not service_dict.get('mem') else service_dict.get('mem')
	#
	# env variables
	#
	env = {}
	env['ETCD_HOST_ADDRESS'] = etcd_host
	#
	# add support for @LABELS
	#
	env['LABELS'] = str(labels)
	env['SERVICE_NAME'] = service_name
	# set up custom environment variables
	custom_env = service_dict.get('environment')
	if custom_env:
		for key in custom_env.keys():
			env[key] = custom_env[key]
	options = []
	constraints = []

	#
	# TODO add support for this
	#
	if service_name == "cassandra":
		options = ["-p", "7000:7000", "-p", "9042:9042", "-p", "9160:9160", "-p", "22000:22", "-p", "5000:5000"]
		ports = []
		constraints = [["hostname", "UNIQUE"]]
	if service_dict.get('volumes'):
		for volume in service_dict['volumes']:
			options.append('-v')
			options.append(volume)

	launched = marathon_api_launch(image, options, app_id, instances, constraints, cpus, mem, env, ports)
	sync_group_config(service_name, labels, config)
	# print launched
	# print instances
	return launched
#
# launches a labeled group
#
def launch_group(service_name, encoded_labels, config):
	# instances = labeled_group.config['instances']
	custom_constraints = config.get('custom_constraints')
	labels = ast.literal_eval(encoded_labels)
	if custom_constraints and custom_constraints == 'fixed-host':
		# must launch as separate apps each one instance
		instances = config.get('instances')
		if instances == None:
			instances = 1
		
		for i in range(0, int(instances)):
			# new_encoded_id = marathon_id + str(i)
			marathon_id = namespacer.encode_marathon_id(service_name, labels, uuid.uuid4())
			launch_app(service_name, marathon_id, config, labels, instances = 1)
	else:
		# just launch app all at once
		marathon_id = namespacer.encode_marathon_id(service_name, labels, uuid.uuid4())
		launch_app(service_name, marathon_id, config, labels)

def marathon_api_launch(image, options, marathon_app_id, instances, constraints, cpus, mem, env, ports):
	#DEBUG
	print 'debug begin'
	print image
	print options
	print 'debug end'
	#DEBUG
	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	marathon_client.create_app(
		container = {
			"image" : str("docker:///"+image), 
			"options" : options
		},
		id = marathon_app_id,
		instances = str(instances),
		constraints = constraints,
		cpus = str(cpus),
		mem = str(mem),
		env = env,
		ports = ports #should be listed in order they appear in dockerfile
	)
	return marathon_app_id

#
# syncs etcd group config
#
def sync_group_config(service, labels, config):
	encoded_labels = namespacer.encode_labels(labels)
	etcd_driver.set_group_config(service, encoded_labels, config)

def unlaunch_app(app_id):
	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	marathon_client.delete_app(app_id)

def unlaunch_group(labeled_group):
	#
	# undeploy all apps
	#
	for app in labeled_group.deploy_ids:
		unlaunch_app(app)


#
# used for scaling. no more delta thing
#
def update_group(service_name, labels, config, existing_marathon_apps, delta = 0):
	custom_constraints = config.get('custom_constraints')
	if custom_constraints:
		print 'cant do custom constraints yet sorry'
	else:
		app_id = existing_marathon_apps[0]
		instances = int(config.get('instances'))
		# if not instances:
		# 	instances = 1+delta
		# else:
		# 	instances = int(instances)+delta
		# config['instances'] = instances
		update_app(app_id, config, instances)
		sync_group_config(service_name, labels, config)
#
# update an app in marathon
#
def update_app(app_id, config, instances = 1):
	#
	# set up marathon client and launch container
	#
	image_string = 'docker:///' + config['image']
	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	app = marathon_client.get_app(app_id)
	#
	# set up options for cassandra TODO this is terrible dawg
	#
	decoded = namespacer.decode_marathon_id(app_id)
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