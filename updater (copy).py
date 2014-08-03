import yaml
from marathon import MarathonClient
import sys
import yaml
import Entities as entities
data = yaml.load(open('mesos.yaml', 'r'))
etcd_host = data['etcd']['host']
marathon_host = data['marathon']['host']
marathon_port = data['marathon']['port']

def update_group(group, delta = 0):
	print 'donothing'
	custom_constraints = group.config.get('custom_constraints')
	if custom_constraints:
		print 'cant do custom constraints yet sorry'
	else:
		app_id = group.deploy_ids[0]
		instances = group.config.get('instances')
		if not instances:
			instances = 1+delta
		else:
			instances = int(instances)+delta
		group.config['instances'] = instances
		update_app(app_id, group.config, instances)
#
# update an app in marathon
#
def update_app(app_id, config, instances = 1):
	#
	# set up marathon client and launch container
	#
	image_string = 'docker:///' + config['image']
	print image_string
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

#
# used in rolling replace
#
def update(marathon_service_id, config,  instances = 1):
	#
	# set up marathon client and launch container
	#
	print 'updating ' + marathon_service_id
	image_string = 'docker:///' + config['image']
	print image_string
	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	app = marathon_client.get_app(marathon_service_id)
	#
	# set up options for cassandra
	#
	options = []
	if "cassandra" in marathon_service_id:
		options = ["-p", "7000:7000", "-p", "9042:9042", "-p", "9160:9160", "-p", "22000:22", "-p", "5000:5000"]
		# ports = []
		# constraints = [["hostname", "UNIQUE"]]

	marathon_client.update_app(
		marathon_service_id,
		app,
		instances = instances,
		container = {
			"image" : image_string, 
			"options" : options
		}
	)
if __name__ == "__main__":
    args = sys.argv
    print 'Welcome Master Liu'
    command = args[1]
    amount = args[2]
    # update_app(command, int(amount))
    update(command, int(amount))

