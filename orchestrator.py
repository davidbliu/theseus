import Entities as entities
import yaml
import uuid
import pickle
import json
import requests
# services = []
#
# load default services from config. these can be modified in-app
# returns a list of services
#


def sync_subscriber():
	data = yaml.load(open('mesos.yaml', 'r'))
	subscriber_address = 'http://'+data['subscriber']['host']+':'+str(data['subscriber']['port'])+'/reconfigure'
	config_data = yaml.load(open('saved_config.yaml', 'r'))
	payload = {'config_data': json.dumps(config_data)}
	# print 'sending post request here...'
	# print subscriber_address
	r = requests.post(subscriber_address, data={'config_data':json.dumps(config_data)})

def update_services(director):
	services = director.services
	data = yaml.load(open('added_configuration.yaml', 'r'))
	print 'updating services'
	for serv in data['services'].keys():
		config = data['services'][serv]
		service = director.services.get(serv)
		if not service:
			print 'this is a new service: '+str(service)
			service = entities.Service(serv)
			director.services[serv] = service
		service.create_labeled_group(config['labels'], config)

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



def test():
	#
	# load director if he exists
	#
	with open('director.pkl', 'rb') as input:
			director = pickle.load(input)

	#
	# clean up director
	#
	director.clean()

	print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
	# update_services(director)
	# presenter = director.services['presenter'].labeled_groups
	# for key in presenter:
	# 	print key
	# 	presenter[key].clean_deploy_ids()
	#
	# save director
	#
	with open('director.pkl', 'wb') as output:
		pickle.dump(director, output, pickle.HIGHEST_PROTOCOL)
	#
	# save current config
	#
	director.flush_config('saved_config.yaml')
	sync_subscriber()

test()