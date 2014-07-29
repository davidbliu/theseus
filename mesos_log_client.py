import requests
import json
import urllib
import yaml
data = yaml.load(open('mesos.yaml', 'r'))
port = 5050
host = data['marathon']['host']
# host    = "54.188.87.91"
# port    = 5050
# task_id = "presenterD.L-testing-D.Lbffc9980-c45c-4392-bd7f-db066c728f77D.L0_1-1406588569619"


def get_log_url(task_id):
	r = requests.get('http://'+host+':'+str(port)+'/state.json')
	state = json.loads(r.content)

	# print state['frameworks']
	frameworks = state['frameworks']
	for framework in frameworks:
		# if framework['name'] ==
		# print framework['name'] 
		# print framework
		if 'marathon' in framework['name']:
			for task in framework['tasks']:
				# print task['id']
				if task['id'] == task_id:
					# print task['id']
					slave_id = task['slave_id']
					framework_id = task['framework_id']
					executor_id = task['executor_id']
					# print task
	if not slave_id:
		print 'no slave id was found'
		return None
	slaves = state['slaves']
	for s in slaves:
		if s['id'] == slave_id:
			slave_host = s['hostname']
			# print s
			slave_name = s['pid'].split('@')[0]
			slave_port = s['pid'].split(':')[1]
			slave_connection_string = 'http://'+slave_host+':'+slave_port+'/'+slave_name+'/state.json'
			# print slave_connection_string
			r = requests.get(slave_connection_string)
			slave_state = json.loads(r.content)
			for fw in slave_state['frameworks']:
				if fw['id'] == framework_id:
					framework = fw
			for ex in framework['executors']:
				# if ex['id'] == executor_id:
					# executor = ex
				for task in ex['tasks']:
					# print task['name']
					if task['name'] == task_id:
						browse_path = ex['directory']
	path = "/#/slaves/"+slave_id+"/browse?path="+browse_path#{browse_path}"
	url = "http://"+host+':'+str(port)+path#{path}"
	return url
	# print url
	# print urllib.urlopen(url).read()

# get_stdout(task_id)