import requests
import json
import urllib
import yaml
import os


port = 5050
host = os.environ['MARATHON_HOST']


def get_log_url(task_id):
	r = requests.get('http://'+host+':'+str(port)+'/state.json')
	state = json.loads(r.content)

	frameworks = state['frameworks']
	for framework in frameworks:
		if 'marathon' in framework['name']:
			for task in framework['tasks']:
				if task['id'] == task_id:
					slave_id = task['slave_id']
					framework_id = task['framework_id']
					executor_id = task['executor_id']
	if not slave_id:
		print 'no slave id was found'
		return None
	slaves = state['slaves']
	for s in slaves:
		if s['id'] == slave_id:
			slave_host = s['hostname']
			slave_name = s['pid'].split('@')[0]
			slave_port = s['pid'].split(':')[1]
			slave_connection_string = 'http://'+slave_host+':'+slave_port+'/'+slave_name+'/state.json'
			r = requests.get(slave_connection_string)
			slave_state = json.loads(r.content)
			for fw in slave_state['frameworks']:
				if fw['id'] == framework_id:
					framework = fw
			for ex in framework['executors']:
				for task in ex['tasks']:
					if task['name'] == task_id:
						browse_path = ex['directory']
	path = "/#/slaves/"+slave_id+"/browse?path="+browse_path
	url = "http://"+host+':'+str(port)+path
	return url
