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
#
# import custom stuff
#
import Entities as entities  
import orchestrator
from flask_bootstrap import Bootstrap

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


	global director
	director = load_director()
	director.clean()
	try:
		query_labels =  str(request.args.get('labels'))
		if query_labels != "None":
			query_labels = query_labels.split(',')
		else:
			query_labels = []
		query_service = str(request.args.get('service'))
		print 'query was '+query_service+' '+ str(query_labels)
	except Exception as failure:
		print failure
		print 'no query parameters'
		query_labels = []
		query_service = None

	groups = []
	services = []
	for s_key in director.services.keys():
		service = director.services.get(s_key)
		for g_key in service.labeled_groups.keys():
			group = service.labeled_groups.get(g_key)
			add = True
			if query_service != 'None' and query_service != group.service.name:
					add = False
			elif query_labels == []:
				add = True
			for query_label in query_labels:
				if query_label not in group.labels:
					add = False
			
			if add:
				groups.append(group)


	return render_template('index.html', director = director, 
										groups = groups, 
										registered = get_etcd_data(query_labels, query_service), 
										query_labels = query_labels, 
										query_service=query_service)

def get_etcd_data(query_labels = [], query_service = 'None'):
	registered = {}
	#
	# loop through services
	#
	etcd_client = etcd.Client(host = str(data['etcd']['host']), port = int(data['etcd']['port']))
	for s_key in director.services.keys():
		if query_service == 'None' or query_service == s_key:
			service = director.services.get(s_key).name
			registered[service] = {}
			try:
				full_instances_dict = etcd_client.read('/'+service).value
				full_instances_dict = ast.literal_eval(full_instances_dict)
				
				for instance in full_instances_dict.keys():
					labels = full_instances_dict[instance]['labels']
					print 'labels are '+str(labels)
					add = True
					for label in query_labels:
						if label not in labels:
							print 'missing a label'+str(label)
							add = False
					if add:
						registered[service][instance] = full_instances_dict[instance]
			except Exception as failure:
				print failure
	return registered
def load_director():
	with open('director.pkl', 'rb') as input:
			director = pickle.load(input)
	return director

if __name__ == '__main__':
	#
	# load default services
	#
	# services = orchestrator.load_services()
	# host = socket.gethostbyname(socket.gethostname())
	global data
	data = yaml.load(open('mesos.yaml', 'r'))
	director = load_director()
	host = 'localhost'
	app.run(port=5001, host=host)