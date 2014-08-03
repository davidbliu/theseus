from marathon import MarathonClient
import time
#
# import launching and updating scripts
#
import launcher as launcher
import updater as updater
import yaml
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
		updater.update(app2_id, app2_config, new_instances)
		
		while num_started < new_instances:
			time.sleep(1)
			print 'waiting for app to start '+str(num_started)
			num_started = num_started_tasks(app2_id)
		#
		# take down old task
		#
		marathon_client.kill_task(app1_id, old_task.id, scale=True)
	marathon_client.delete_app(app1_id)

def rolling_replace_group(old_group, new_group):
	new_deploy_ids = []
	for index, old_app_id in enumerate(old_group.deploy_ids):
		# print old_app_id
		# print 'that was the old app id'
		new_app_id = new_group.encode_marathon_id+str(index)
		new_deploy_ids.append(new_app_id)
		# print new_app_id
		# print 'that was the new app id'
		rolling_replace_app(new_group.service.name, old_app_id, new_app_id, new_group.config, new_group.labels)
		print "replaced app.............................................."
	new_group.deploy_ids = new_deploy_ids
#
# procedure: start service2, stop service1...continue until all of service 1 is down
# remove service 1
# how does haproxy or other servicse know?
# currently: watch an etcd key
# another option: send sigals
# TODO thing about this
#
def rolling_replace(app1_id, group2):
	print '    replacing '+app1_id+' with '+group2.service.name
	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	app1 = marathon_client.get_app(app1_id)
	# print app1
	old_tasks = app1.tasks
	# print old_tasks
	

	launcher.launch(group2.service.name, group2.encode_marathon_id, group2.config, instances = 0)
	new_app = marathon_client.get_app(group2.encode_marathon_id)

	for old_task in old_tasks:
		#
		# replace each old task with a new task of the new app
		#
		print old_task.host
		num_started = num_started_tasks(group2.encode_marathon_id)
		new_instances = num_started+1
		print 'there are currently '+str(num_started)+' instances'
		print 'we want '+str(new_instances)+' instances'
		# add 1 instance of new task
		updater.update(group2.encode_marathon_id, group2.config, new_instances)
		
		while num_started < new_instances:
			time.sleep(1)
			print 'waiting for app to start '+str(num_started)
			num_started = num_started_tasks(group2.encode_marathon_id)
		#
		# take down old task
		#
		marathon_client.kill_task(app1.id, old_task.id, scale=True)
	marathon_client.delete_app(app1.id)



def num_started_tasks(app_id):
	count = 0
	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	app = marathon_client.get_app(app_id)
	tasks = app.tasks
	for task in tasks:
		if task.started_at:
			count += 1
	return count
