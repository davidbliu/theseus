import ast
import uuid 
import yaml

id_separator = 'D.L'


def encode_labels(labels):
	return str(sorted(labels)).replace(' ', '')
def encode_marathon_id(service_name, labels, version_string):
	# start with service
	version_string = str(version_string)
	marathon_id_string = str(service_name)
	label_string = str(labels)[:-1][1:].replace("'", "-").replace(",", ".").replace(" ", "")
	marathon_id =  marathon_id_string + id_separator + label_string + id_separator + version_string + id_separator

	return marathon_id


# 
# gets a service and labels from marathon id
#
def decode_marathon_id(marathon_id):
	# split up id
	id_split = marathon_id.split(id_separator)
	service_name = str(id_split[0])
	labels = ast.literal_eval('['+id_split[1].replace("-", "'").replace(".", ",")+']')
	version = str(id_split[2])
	return {'service':service_name, 'labels':labels, 'version':version}

# def get_version(task_id):
def get_app_from_task(task_id):
	id_split = task_id.split(id_separator)
	truncated =  id_split[:-1]
	app_string = ''
	for piece in truncated:
		app_string += piece + id_separator
	return app_string