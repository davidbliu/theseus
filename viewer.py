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
import Entities as entities  
import orchestrator
import mesos_log_client
from flask_bootstrap import Bootstrap

import etcd_driver

app = Flask(__name__)
Bootstrap(app)
services = []
#
# monitor all processes 
#

#
# recieve post request and write data into kafka
#
@app.route('/', methods=['GET', 'POST'])
def root():
	#
	# no queries for now
	#
	print 'hi'
	data = get_all_etcd_data()
	# services_list = data.keys()
	mesos_data = yaml.load(open('mesos.yaml', 'r'))
	etcd_host = mesos_data['etcd']['host']
	marathon_host = mesos_data['marathon']['host']
	marathon_port = mesos_data['marathon']['port']

	marathon_url = 'http://'+marathon_host+':'+str(marathon_port)
	mesos_url = 'http://'+marathon_host+':5050'
	etcd_url = 'http://'+etcd_host+':4001'
	# return jsonify(result={'status':200})
	return render_template('viewer.html', data = data,
										  mesos_url = mesos_url,
										  marathon_url = marathon_url, 
										  etcd_url = etcd_url)

#
# AJAX stuff
#
@app.route('/get_log_url',methods=['GET','POST'])
def get_log_url():
	print 'here i am'
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

	# global data
	data = yaml.load(open('mesos.yaml', 'r'))
	# director = load_director()
	host = 'localhost'

	print 'running your app on '+str(host)

	app.run(port=5001, host=host)
