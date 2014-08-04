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
