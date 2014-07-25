import yaml
from marathon import MarathonClient
import requests
import json
data = yaml.load(open('mesos.yaml', 'r'))
etcd_host = data['etcd']['host']
marathon_host = data['marathon']['host']
marathon_port = data['marathon']['port']
#
# make sure subscriber has same config info as workstation
#
def sync_subscriber():
	subscriber_address = 'http://'+data['subscriber']['host']+':'+str(data['subscriber']['port'])+'/reconfigure'
	config_data = yaml.load(open('config.yaml', 'r'))
	payload = {'config_data': json.dumps(config_data)}
	# print 'sending post request here...'
	# print subscriber_address
	r = requests.post(subscriber_address, data={'config_data':json.dumps(config_data)})

#
# launches a single app. you may need to launch several apps for fixed host groups
#
def launch_app(service_name, app_id, config, labels = [], instances = -1):
	print 'launching ' + service_name
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

	return marathon_api_launch(image, options, app_id, instances, constraints, cpus, mem, env, ports)

#
# launches a labeled group
#
def launch_group(labeled_group):
	# instances = labeled_group.config['instances']
	custom_constraints = labeled_group.config.get('custom_constraints')
	if custom_constraints and custom_constraints == 'fixed-host':
		print 'oh noes FIXED HOST constrain what am i gonna do cry cry'
		# must launch as separate apps each one instance
		instances = labeled_group.config.get('instances')
		if instances == None:
			instances = 1
		deploy_ids = []
		for i in range(0,int(instances)):
			new_encoded_id = labeled_group.encode_marathon_id + str(i)
			deploy_id = launch_app(labeled_group.service.name, new_encoded_id, labeled_group.config, labeled_group.labels, instances = 1)
			deploy_ids.append(deploy_id)
		labeled_group.deploy_ids = deploy_ids

	else:
		# just launch app all at once
		launch_app(labeled_group.service.name, labeled_group.encode_marathon_id, labeled_group.config, labeled_group.labels)
		labeled_group.deploy_ids = [labeled_group.encode_marathon_id]

def marathon_api_launch(image, options, marathon_app_id, instances, constraints, cpus, mem, env, ports):
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

def unlaunch_app(app_id):
	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	marathon_client.delete_app(app_id)

def unlaunch_group(labeled_group):
	#
	# undeploy all apps
	#
	for app in labeled_group.deploy_ids:
		unlaunch_app(app)