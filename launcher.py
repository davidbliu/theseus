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
# launches a labeled group
#
def launch(service, service_encoded_id,  config, labels = [], instances = -1):
	print 'launching ' + service
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
	env['SERVICE_NAME'] = service
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
	if service == "cassandra":
		options = ["-p", "7000:7000", "-p", "9042:9042", "-p", "9160:9160", "-p", "22000:22", "-p", "5000:5000"]
		ports = []
		constraints = [["hostname", "UNIQUE"]]
	if service_dict.get('volumes'):
		for volume in service_dict['volumes']:
			options.append('-v')
			options.append(volume)
	
	# print 'here are your instance details'
	# print type(service)
	# print service_encoded_id
	# print type(instances)
	# print constraints
	# print cpus
	# print mem
	# print env
	# print ports
	# print image
	# print options
	# print labels
	# print type(labels)
	# print 'end of instance details'
	custom_constraints = service_dict.get('custom_constraints')
	if custom_constraints:
		print 'these are your constraints '+str(custom_constraints)
		if custom_constraints == 'fixed-host':
			deploy_ids = []
			for i in range(0,int(instances)):
				new_encoded_id = service_encoded_id + str(i)
				deploy_id = marathon_api_launch(image, options, new_encoded_id, 1, constraints, cpus, mem, env, ports)
				deploy_ids.append(deploy_id)
			return deploy_ids
		else:
			print 'no other custom constraints implemented yet!'
	else:
		deploy_id = marathon_api_launch(image, options, service_encoded_id, 1, constraints, cpus, mem, env, ports)
		return [deploy_id]

	#
	# set up marathon client and launch container
	#
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
