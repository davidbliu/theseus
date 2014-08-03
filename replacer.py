from marathon import MarathonClient
import time
#
# import launching and updating scripts
#
import launcher, updater, namespacer
import yaml
import ast
import uuid 

data = yaml.load(open('mesos.yaml', 'r'))
etcd_host = data['etcd']['host']
marathon_host = data['marathon']['host']
marathon_port = data['marathon']['port']


#
# replaces app with another app. many may be required for fixed host constraint
#
def rolling_replace_app(service_name, app1_id, app2_id, app2_config, labels):
	print '    replacing '+app1_id+' with '+app2_id
	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	app1 = marathon_client.get_app(app1_id)
	old_tasks = app1.tasks
	# launcher.launch(group2.service.name, group2.encode_marathon_id, group2.config, instances = 0)
	launcher.launch_app(service_name, app2_id, app2_config, labels, instances = 0 )
	new_app = marathon_client.get_app(app2_id)
	for old_task in old_tasks:
		#
		# replace each old task with a new task of the new app
		#
		num_started = num_started_tasks(app2_id)
		new_instances = num_started+1
		# add 1 instance of new task
		launcher.update_app(app2_id, app2_config, new_instances)
		
		while num_started < new_instances:
			time.sleep(1)
			print 'waiting for app to start '+str(num_started)
			num_started = num_started_tasks(app2_id)
		#
		# take down old task
		#
		marathon_client.kill_task(app1_id, old_task.id, scale=True)
	marathon_client.delete_app(app1_id)

def rolling_replace_group(service_name, labels, config, existing_apps):
	for old_app_id in existing_apps:
		# make new version
		version = uuid.uuid4()
		new_app_id = namespacer.encode_marathon_id(service_name, labels, version)
		rolling_replace_app(service_name, old_app_id, new_app_id, config, labels)




def num_started_tasks(app_id):
	count = 0
	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	app = marathon_client.get_app(app_id)
	tasks = app.tasks
	for task in tasks:
		if task.started_at:
			count += 1
	return count
