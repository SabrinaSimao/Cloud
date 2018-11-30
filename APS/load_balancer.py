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
from datetime import datetime, timedelta, timezone

delta = timedelta(seconds=400)

global size
size = int(sys.argv[1])

how_many = size

## BEGIN THREAD##
def loop():
	while True:
		healthcheck()
		print("ping...\n")
		time.sleep(30)
		



##END THREAD##
	
#Client

client = boto3.client('ec2')

#Service

ec2 = boto3.resource('ec2')


key_name = 'Sa_Key'

group_name = 'APS'

#My public key
pub_key = open("./project_key.pub", "r")

ap.create_keypair(client, pub_key, key_name)
ap.create_security_group(client, group_name)

##Dictionary of Public IPs##


inside = ap.describe_instance(client)
 

public_ips = ap.make_dic_of_pub_ips_filtered(client, inside)

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def catch_all(path):
    
	if request.method == 'GET':
		print("\nMethod is GET\n")
		print("\nPATH IS {0}\n".format(path))
		instance_id, server_ip = random.choice(list(public_ips.items()))
		r = requests.get('http://' +str(server_ip[0])+':5000/' + path)
		return jsonify({"status": "OK","data": r.text}, )

	else:
		#page_not_found(error)
		return jsonify({"status": "NOT OK"})

def healthcheck():
	global how_many
	global public_ips
	global ec2
	global client
	global key_name
	global group_name

	#just one instance at a time, so it doesnt overload anything
	if how_many < size:
		how_many += 1
		print("\nYou have less instances then you should..... Lets create another one\n")
		ap.create_instance(ec2, key_name, group_name)
		print("\nHow many instances are OK: {0}".format(how_many))

	for key, value in public_ips.items():
		
		print ("Waiting healthcheck request from instance {0}".format(key))
		print("\n Ip is: {0}".format(str(value[0])))
		Now = datetime.now(timezone.utc)
		print((Now - value[2]))
		if ((Now - value[2]) < delta):
			print("TOO SOON EXECUTUS\n")
			
		else:
			try:
				r = requests.get('http://' +str(value[0])+':5000/healthcheck', timeout=3.0)   ##TIME OUT##
				print ("Finishing healthcheck request from instance {0}".format(key))
				if (r.status_code == 200):
					print("\nEverything OK :) \n")
					public_ips[key] = [value[0], 1, value[2]]
				else:
					#you should never enter here
					print("\nJUMPING OUT SOMETHING BROKE\n")
					public_ips[key] = [value[0], 0, value[2]]
					break
			except:
					print("\nTimeout is true, instance is dead.\n")
					public_ips[key] = [value[0], 0, value[2]]
					print(key)
	
	for key, value in public_ips.items():
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
			print("Instance {0} is running smoothly".format(key))

	print ("Finishing healthcheck..............")
	running_instance = ap.describe_instance(client)

	public_ips = ap.make_dic_of_pub_ips_filtered(client, running_instance)
	time.sleep(15)

if __name__ == '__main__':
	t = Thread(target=loop)
	t.start()
	app.run(debug=False, host="0.0.0.0")

