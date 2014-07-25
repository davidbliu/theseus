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

	groups = []
	for service in services:
		for group in service.labeled_groups:
			groups.append(group)
	return render_template('index.html', services = services, groups = groups)


if __name__ == '__main__':
    print 'Starting APP on port 5000'
    #
    # load default services
    #
    services = orchestrator.load_services()
    # host = socket.gethostbyname(socket.gethostname())
    host = 'localhost'
    app.run(port=5000, host=host)