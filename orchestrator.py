import Entities as entities
import yaml
import uuid
import pickle
# services = []
#
# load default services from config. these can be modified in-app
# returns a list of services
#
def load_services():
	services = []
	data = yaml.load(open('configuration.yaml', 'r'))
	for serv in data['services'].keys():
		# print service
		# image = data['services'][serv]['image
		config = data['services'][serv]
		# create labeled group
		service = entities.Service(serv)
		labeled_group = service.create_labeled_group(labels = ['main'], 
													config = config)
		# print labeled_group.encode_marathon_id
		# print entities.decode_marathon_id(labeled_group.encode_marathon_id)
		# print labeled_group.config
		# labeled_group.deploy()
		# print 'deployed'
		services.append(service)
	return services

def get_service_by_name(name, services):
	for service in services:
		if service.name == name:
			return service
	return None

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

	update_services(director)
	#
	# save director
	#
	with open('director.pkl', 'wb') as output:
		pickle.dump(director, output, pickle.HIGHEST_PROTOCOL)
	#
	# save current config
	#
	director.flush_config('saved_config.yaml')

def test2():
	print 'hi'
test()