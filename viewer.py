import argparse
import atexit
import sys
import urlparse
import yaml
from flask import Flask, request, jsonify, render_template
import marathon
import urllib2
import etcd
import socket
import os
import shutil
import subprocess
import ast
import pickle
import json
#
# import custom stuff
#
import orchestrator
import mesos_log_client
from flask_bootstrap import Bootstrap

import etcd_driver

app = Flask(__name__)
Bootstrap(app)


@app.route('/', methods=['GET', 'POST'])
def root():
	#
	# no queries for now
	#
	print 'hi'
	data = get_all_etcd_data()
	marathon_host = os.environ['MARATHON_HOST']
	marathon_port = os.environ['MARATHON_PORT']
	etcd_host = os.environ['ETCD_HOST_ADDRESS']

	marathon_url = 'http://'+marathon_host+':'+str(marathon_port)
	mesos_url = 'http://'+marathon_host+':5050'
	etcd_url = 'http://'+etcd_host+':4001'
	return render_template('viewer.html', data = data,
										  mesos_url = mesos_url,
										  marathon_url = marathon_url, 
										  etcd_url = etcd_url)


@app.route('/deploy', methods=['POST'])
def deploy():
	print 'alskdfjlaksjdflakjsdlfkjalskdjflaskdjflakjdslfjalskdjj'
	print request
	print 'that was the request'
	config_data =  request.data

	print config_data
	config_data = ast.literal_eval(config_data)

	orchestrator.update_services(config_data)
	return jsonify(result={'status':200})
#
# AJAX stuff
#
@app.route('/get_log_url',methods=['GET','POST'])
def get_log_url():
	try:
		task_id =  str(request.args.get('task_id'))
		return json.dumps(mesos_log_client.get_log_url(task_id))
	except Exception as failure:
		print failure
		return jsonify(result={'status':500})

#
# service keys group keysgroup containers list
#
def get_all_etcd_data():
	data = {}
	service_names = etcd_driver.get_service_names()
	for service_name in service_names:
		service_dict = {}
		service_groups = etcd_driver.get_service_groups(service_name)
		for group in service_groups:
			if etcd_driver.group_exists(service_name, group) and group != "":
				print 'adding this group'
				print service_name
				print group
				group_containers = []
				for container_name in etcd_driver.get_group_container_names(service_name, group):
					container_data = {}
					container_data['name'] = container_name
					container_data['info'] = etcd_driver.get_container_info(service_name, group, container_name)
					group_containers.append(container_data)
				group_config = etcd_driver.get_group_config(service_name, group)
				service_dict[group] = {'containers': group_containers, 'config':group_config}
		data[service_name]  = service_dict
	return data

if __name__ == '__main__':


	# print 'starting ssh'
	# os.system("/usr/sbin/sshd -D &")

	host = 'localhost'
	# host = socket.gethostbyname(socket.gethostname())
	print 'running your app on '+str(host)

	app.run(port=5001, host=host)
