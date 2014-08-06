# import Entities as entities
import etcd_driver
import yaml
import uuid
import json
import requests
import argparse
#
# import modules
#
import namespacer, launcher, replacer

#
# service keys group keysgroup containers list
#
def get_all_data():
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
			service_dict[group] = group_containers
		data[service_name]  = service_dict
	return data


#
# consume data, if new services, create new
# if old and old group, replace it
#
def update_services(data):
	print 'updating services with this data'
	print data
	print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
	if data.get('deploy'):
		for serv in data['deploy'].keys():
			config = data['deploy'][serv]
			#
			# create new group
			#
			service_name = serv
			labels = data['deploy'][serv]['labels']
			encoded_group_labels = namespacer.encode_labels(labels)
			if etcd_driver.group_exists(service_name, encoded_group_labels):
				old_config = etcd_driver.get_group_config(service_name, encoded_group_labels)
				unmatched_items = set(convert_dict_values_to_strings(old_config).items()) ^ set(convert_dict_values_to_strings(config).items())
				should_update = True
				print unmatched_items
				for item in unmatched_items:
					if item[0] != 'instances':
						should_update = False
						print type(item[1])
						print item[1]
				if len(unmatched_items)==0:
					should_update = False
				if should_update:
					print 'updating group...'
					scale(service_name, labels, config)
				else:
					print 'rolling update...'
					deploy_existing(service_name, labels, config)
			else:
				print 'creating new group...'
				deploy_new(service_name, encoded_group_labels, config)

	if data.get('remove'):
		for serv in data['remove'].keys():
			service_name = serv
			labels = data['remove'][serv]['labels']
			print 'removing...'
			undeploy(service_name, labels)
			print '\t'+'removed '+str(service_name)+' '+str(labels)

def deploy_new(service_name, encoded_group_labels, config):
	# custom constraints handled in launcher
	launcher.launch_group(service_name, encoded_group_labels, config)

def get_existing_marathon_apps(service_name, encoded_group_labels):
	existing_containers = etcd_driver.get_group_container_names(service_name, encoded_group_labels)
	existing_marathon_apps = []
	for container in existing_containers:
		app_id = namespacer.get_app_from_task(container)
		if app_id not in existing_marathon_apps:
			existing_marathon_apps.append(app_id)
	return existing_marathon_apps
def deploy_existing(service_name, labels, config):
	encoded_group_labels = namespacer.encode_labels(labels)
	existing_marathon_apps = get_existing_marathon_apps(service_name, encoded_group_labels)
	#
	# update existing apps
	#
	replacer.rolling_replace_group(service_name, labels, config, existing_marathon_apps)
def undeploy(service_name, labels):
	encoded_group_labels = namespacer.encode_labels(labels)
	existing_marathon_apps = get_existing_marathon_apps(service_name, encoded_group_labels)
	for app in existing_marathon_apps:
		launcher.unlaunch_app(app)
def scale(service_name, labels, config):
	encoded_group_labels = namespacer.encode_labels(labels)
	existing_marathon_apps = get_existing_marathon_apps(service_name, encoded_group_labels)
	launcher.update_group(service_name, labels, config, existing_marathon_apps)

def manual_update(config_file = 'added_configuration.yaml'):
	data = yaml.load(open(config_file, 'r'))
	# print data
	update_services(data)


#
# helper methods
#
def convert_dict_values_to_strings(dictionary):
	new_dict = {}
	for key in dictionary.keys():
		curr_item = dictionary[key]
		if type(curr_item) == dict:
			# print 'item is a dict'
			sorted_keys = sorted(curr_item.keys())
			keystring = str(sorted_keys)
			itemlist = []
			for k in sorted_keys:
				itemlist.append(curr_item[k])
			itemstring = str(itemlist)
			new_dict[key] = keystring+itemstring
		else:
			new_dict[key] = str(curr_item)
	return new_dict

if __name__ == "__main__":
	print 'Welcome Master Liu'
	parser = argparse.ArgumentParser(description='Theseus')
	parser.add_argument('-f', '--config-file', required=True, help='configuration file')
	args = parser.parse_args()
	config_file = args.config_file
	manual_update(config_file)
	# data = yaml.load(open('added_configuration.yaml', 'r'))
	# service_name = 'ingestor'
	# labels = data['services'][service_name]['labels'
	# undeploy(service_name, labels)
	#
	# try update functionality
	#
