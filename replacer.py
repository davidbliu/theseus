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
# procedure: start service2, stop service1...continue until all of service 1 is down
# remove service 1
# how does haproxy or other servicse know?
# currently: watch an etcd key
# another option: send sigals
# TODO thing about this
#
def rolling_replace(app1_id, group2):
	print 'replacing '+app1_id+' with '+group2.service.name
	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	app1 = marathon_client.get_app(app1_id)
	print app1
	old_tasks = app1.tasks
	print old_tasks
	

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

def num_started_tasks(service):
	count = 0
	marathon_client = MarathonClient('http://' + str(marathon_host) + ':' + str(marathon_port))
	app = marathon_client.get_app(service)
	tasks = app.tasks
	for task in tasks:
		if task.started_at:
			count += 1
	return count
