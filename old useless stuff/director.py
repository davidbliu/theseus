import etcd_driver
import uuid
import ast
#
# load director from etcd 
#
class Director:

	def __init__(self, services = {}):
		self.services = services
	def clean(self):
		print '.'
	def find_labeled_group(self, service_name, labels):
		print '.'
	def flush_config(self, outfile):
		print '.'
	def dump(self):
		with open('director.pkl', 'wb') as output:
			pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

	def print_director(self):
		for service_name in self.services.keys():
			print 'service '+service_name
			groups = self.services[service_name].labeled_groups
			for group_key in groups:
				print '\t'+group_key
				container_names = groups[group_key].containers
				print '\t'+str(container_names)


class Service:

	def __init__(self, name):
		self.name = name
		self.labeled_groups = {}

	@property
	def name(self):
		return self.name

	def __repr__(self):
		return self.name

	def group_exists(self, labels):
		print '.'

	def create_labeled_group(self, labels, config):
		labels = sorted(labels)
		existing_group = self.labeled_groups.get(str(labels))
		labeled_group = LabeledGroup(self, labels, config)
		self.labeled_groups[str(labels)] = labeled_group
		return labeled_group

	def remove_undeployed_groups(self):
		print '.'

	def get_deployed_labeled_group_ids(self, labels):
		print '.'

class LabeledGroup:

	id_separator = 'D.L'

	def __init__(self, service, labels, config, image = 'default'):
		self.service = service
		self.labels = labels
		self.image = image
		self.config = config
		self.version = uuid.uuid4()
		self.deploy_ids = []

	def __repr__(self):
		return str(self.service) + ' labels ' + str(self.labels) + ' version '+str(self.version)

	@property
	def config_yaml(self):
		print '.'

	@property
	def encode_marathon_id(self):
		# start with service
		marathon_id_string = str(self.service)
		label_string = str(self.labels)[:-1][1:].replace("'", "-").replace(",", ".").replace(" ", "")
		version_string = str(self.version)
		marathon_id =  marathon_id_string + LabeledGroup.id_separator + label_string + LabeledGroup.id_separator #+ version_string + LabeledGroup.id_separator

		return marathon_id

	#
	# list of names of containers
	#
	@property
	def containers(self):
		# return self.labels
		return etcd_driver.get_group_container_names(self.service.name, str(sorted(self.labels)))
	@property
	def is_deployed(self):
		print '.'
	
# 
# gets a service and labels from marathon id
#
def decode_marathon_id(marathon_id):
	# split up id
	id_split = marathon_id.split(LabeledGroup.id_separator)
	service_name = str(id_split[0])
	labels = ast.literal_eval('['+id_split[1].replace("-", "'").replace(".", ",")+']')
	version = str(id_split[2])
	return {'service':service_name, 'labels':labels, 'version':version}

def load_director():
	director = Director()
	service_names = etcd_driver.get_service_names()
	for service_name in service_names:
		service = Service(service_name)
		groups = etcd_driver.get_service_groups(service_name)
		for group in groups:
			config = etcd_driver.get_group_config(service_name, group)
			service.create_labeled_group(ast.literal_eval(group), config)
		#
		# put service into director
		#
		director.services[service_name] = service
	director.print_director()


load_director()