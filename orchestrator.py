import Entities as entities
import yaml
import uuid
import pickle
import json
import requests
import argparse
# services = []
#
# load default services from config. these can be modified in-app
# returns a list of services
#


def sync_subscriber():
	print 'syncing subscriber'
	data = yaml.load(open('mesos.yaml', 'r'))
	subscriber_address = 'http://'+data['subscriber']['host']+':'+str(data['subscriber']['port'])+'/reconfigure'

	mesos_data = yaml.load(open('mesos.yaml', 'r'))
	config_data = yaml.load(open('saved_config.yaml', 'r'))
	config_data = dict(mesos_data.items() + config_data.items())
	payload = {'config_data': json.dumps(config_data)}
	# print 'sending post request here...'
	# print subscriber_address
	r = requests.post(subscriber_address, data={'config_data':json.dumps(config_data)})

def load_config():
	data = yaml.load(open('added_configuration.yaml', 'r'))
	return data

def update_services(director, data):
	services = director.services
	if data.get('services') is None:
		return
	for serv in data['services'].keys():
		config = data['services'][serv]
		service = director.services.get(serv)
		if not service:
			service = entities.Service(serv)
			director.services[serv] = service
		service.create_labeled_group(config['labels'], config)
	#
	# save director
	#
	director.dump()
	#
	# save current config
	#
	director.flush_config('saved_config.yaml')
	sync_subscriber()

def print_topo(director):
	print 'wtf'
	for service in director.services:
		for labeled_group in service.labeled_groups:
			labels = labeled_group.labels
			print 'service '+str(service)+ 'labels '+str(labels)
			print  service.get_deployed_labeled_group_ids(labels)
			print [labeled_group.encode_marathon_id]
			print labeled_group.is_deployed
	print 'here are your groups'
	for group in director.find_labeled_groups('cassandra', ['main', 'tiny']):
		print group

# def flush_data():

def load_director():
	director = None
	with open('director.pkl', 'rb') as input:
			director = pickle.load(input)
	return director


def deploy():
	#
	# load director if he exists
	#
	director = load_director()
	#
	# clean up director
	#
	director.clean()
	print '>>>>>>>>>>>>>> CLEAN >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
	update_services(director, load_config())
	#
	# save director
	#
	director.dump()
	#
	# save current config
	#
	director.flush_config('saved_config.yaml')
	sync_subscriber()

def undeploy(service_name, labels = []):
	director = load_director()
	director.clean()
	print director.services
	serv = director.services.get(service_name)
	if serv is None:
		print 'serv is none'
		return
	group = serv.labeled_groups.get(str(sorted(labels)))
	if group:
		group.undeploy()
		print 'undeployed'
	else:
		print 'no group'
	director.dump()
	director.flush_config('saved_config.yaml')
	sync_subscriber()

if __name__ == "__main__":
    print 'Welcome Master Liu'
    sync_subscriber()
    parser = argparse.ArgumentParser(description='Docker Orchestrator Launcher')
    parser.add_argument('-s', '--service-name', required=True, help='service name')
    parser.add_argument('-c', '--command', required=True, help='command')
    parser.add_argument('-l', '--labels', required=False, help='command')
    args = parser.parse_args()
    service = args.service_name
    command = args.command

    if command == 'deploy':
    	deploy()
    elif command == 'undeploy':
    	# labels = ['dragons','fairydust','hello','ponies']
    	label_list = args.labels
    	if label_list is None or label_list is "":
    		labels = []
    	else:
    		labels = label_list.split(',')
    	service = 'my_name_is_david'
    	undeploy(service, labels)
    	# undeploy(service)
    	#
    	# test undeploy functionalitiy
    	#
