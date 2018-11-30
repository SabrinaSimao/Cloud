import boto3
import pprint
from flask import Flask, request, jsonify
import json
import random
import requests
import time
import aps3_functions as ap
from threading import Thread, Timer
import sys

global size
size = int(sys.argv[1])

global how_many
how_many = size

## BEGIN THREAD##
def loop():
	while True:
		healthcheck()
		time.sleep(10)
		print("ping...\n")



##END THREAD##
	
#Client
global client
client = boto3.client('ec2')

#Service
global ec2
ec2 = boto3.resource('ec2')

global key_name
key_name = 'Sa_Key'
global group_name
group_name = 'APS'

#My public key
pub_key = open("./project_key.pub", "r")

ap.create_keypair(client, pub_key, key_name)
ap.create_security_group(client, group_name)

##Dictionary of Public IPs##


inside = ap.describe_instance(client)

global public_ips 

public_ips = ap.make_dic_of_pub_ips_filtered(client, inside)

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    

	if request.method == 'POST':
		print("\nMethod is POST\n")
		instance_id, server_ip = random.choice(list(public_ips.items()))
		value = json.loads(request.data.decode("utf-8"))
		r = requests.post('http://' +str(server_ip[0])+':5000/' + path, json = value)
		return jsonify({"status": "OK","data": r.text})

	elif request.method == 'GET':
		print("\nMethod is GET\n")
		print("\nPATH IS {0}\n".format(path))
		instance_id, server_ip = random.choice(list(public_ips.items()))
		r = requests.get('http://' +str(server_ip[0])+':5000/' + path)
		return jsonify({"status": "OK","data": r.text}, )

	elif request.method =='DELETE':
		print("\nMethod is DELETE\n")
		instance_id, server_ip = random.choice(list(public_ips.items()))
		value = json.loads(request.data.decode("utf-8"))
		r = requests.delete('http://' +str(server_ip[0])+':5000/' + path, json = value)
		return jsonify({"status": "OK","data": r.text})

	elif request.method =='PUT':
		print("\nMethod is PUT\n")
		instance_id, server_ip = random.choice(list(public_ips.items()))
		value = json.loads(request.data.decode("utf-8"))
		r = requests.put('http://' +str(server_ip[0])+':5000/' + path , json = value)
		return jsonify({"status": "OK","data": r.text})

	else:
		#page_not_found(error)
		return jsonify({"status": "NOT OK"})

def healthcheck():

	#refactor dic of public ips
	running_instance = ap.describe_instance(client)
	running_inside = running_instance['Reservations']

	public_ips = ap.make_dic_of_pub_ips_filtered(client, inside)
	if how_many < size:
		how_many += 1
		ap.create_instance(ec2, key_name, group_name)
		print("\nHow many instances are OK: {0}".format(how_many))

	for key, value in public_ips.items():
		
		print ("Waiting healthcheck request from instance {0}".format(key))
		print("\n Ip is: {0}".format(str(value[0])))

		try:
			r = requests.get('http://' +str(value[0])+':5000/healthcheck', timeout=3.0)   ##TIME OUT##
			print ("Finishing healthcheck request from instance {0}".format(key))
			if (r.status_code == 200):
				print("\nEverything OK :) \n")
				public_ips[key] = [value[0], 1]
			else:
				print("\nJUMPING OUT SOMETHING BROKE\n")
				public_ips[key] = [value[0], 0]
		except:
				print("\nTimeout is true, instance is dead.\n")
				public_ips[key] = [value[0], 0]
				print(key)
	
	time.sleep(30)

	for key, value in public_ips.items():
		print(public_ips)
		if (int(value[1]) == 0):
		how_many -= 1
		print("\nHow many instances are OK: {0}".format(how_many))
			try:
				deleted = client.terminate_instances(
				InstanceIds=[
					str(key)
				])
				print("\n....Terminating Instance....\n")
			except IndexError:
				print("\nNo Instance with this tag is running. It may have terminated\n")
		else:
			return("Instance {0} is running smoothly".format(InstanceId))

	print ("Finishing healthcheck..............")


if __name__ == '__main__':
	t = Thread(target=loop)
	t.start()
	app.run(debug=True, host="0.0.0.0")

