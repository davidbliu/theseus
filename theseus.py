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
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
data = None
#
# monitor all processes 
#
@app.route('/monitor', methods=['GET'])
def monitor():
	import guestutils
	nodes = guestutils.get_node_list('ingestor', ports=['api'])
	print 'these are your nodes'
	print nodes
	paths = []
	for node in nodes:
		paths.append(str(node)+'/stats')
	return render_template('performance.html', nodes = paths)
#
# recieve post request and write data into kafka
#
@app.route('/', methods=['GET', 'POST'])
def root():
	#
	# get etcd info
	#
	registered = {}
	#
	# loop through services
	#
	etcd_client = etcd.Client(host = str(data['etcd']['host']), port = int(data['etcd']['port']))
	for service in data['services'].keys():
		registered[service] = {}
		print 'trying this key '+str(service)
		try:
			full_instances_dict = etcd_client.read('/'+service).value
			full_instances_dict = ast.literal_eval(full_instances_dict)
			for instance in full_instances_dict.keys():
				registered[service][instance] = full_instances_dict[instance]
			# print registered
		except Exception as failure:
			print failure
			print 'cannot read this key from etcd'
	#
	# publish information on config file
	#
	info_dict = {}
	for service in data['services'].keys():
		info = data['services'][service]
		info_dict[service] = info
	return render_template('theseus.html', registered = registered, info_dict = info_dict)


if __name__ == '__main__':
    print 'Starting Theseus on port 5000'
    
    global data
    data = yaml.load(open('config.yaml', 'r'))
    host='localhost'
    # host = socket.gethostbyname(socket.gethostname())
    app.run(port=5000, host=host)