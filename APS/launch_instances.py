import boto3
import pprint
import sys

size = int(sys.argv[1])
#My public key
pub_key = open("./project_key.pub", "r")

#Client
client = boto3.client('ec2')
print('\n')
print('ec2 Cliente: ')
print(client)
print('\n')

#Service
ec2 = boto3.resource('ec2')
print('\n')
print('ec2 Resource: ')
print(ec2)
print('\n')


#Delete Instance if Running
instance = client.describe_instances(
    Filters= [{'Name': 'tag:Owner', 'Values': ['Sabrina']}]
)

#list of all instances that comply with filter above
inside = instance['Reservations']

public_ips = {}

for i in range(len(inside)):
	instance_dic = inside[i]
	try:
		public_ip = instance_dic['Instances'][0]['PublicIpAddress']
		InstanceId = instance_dic['Instances'][0]['InstanceId']
		public_ips[InstanceId] = public_ip
		print(InstanceId)
		deleted = client.terminate_instances(
		InstanceIds=[
		    InstanceId
		])
		print("\nTerminating Instance.\n")
		print(deleted)
	except IndexError:
		print("\nNo Instance with this tag is running. It may have terminated\n")
	except KeyError:
			print("An instance was found and it has no Public Ip Adress. It may have terminated")

print("\nDic of Public Ips: \n")
print(public_ips)
print("\n.......Preparing to Launch New Instance.........\n")


#pprint.pprint(instance)


#Nome da Chave que Usarei Sempre e todo o Sempre
Key_Name = 'Sa_Key'

keypairs = client.describe_key_pairs()
print("\nKeyPairs: \n")
print(keypairs)


#Delete KeyPair
print("\nTry to Delete KeyPair\n")
try:
	key_pair_delete = client.delete_key_pair(
	    KeyName=Key_Name
	)
	print("\nDeleting KeyPair\n")
except:
	print("\nInstance is Using KeyPair, skipping Delete\n")

print("\nCreating New KeyPair\n")
#Import KeyPair
key_pair = client.import_key_pair(
    KeyName=Key_Name,
    PublicKeyMaterial=pub_key.read()
)

print('\n')
print('keypair: ')
pprint.pprint(key_pair)
print('\n')

#Group Name
group_name = 'APS'

print("\nTrying to Delete Security Group\n")
#Delete Security Group
try:
	delete_group = client.delete_security_group(
    	GroupName=group_name
	)
	print("\nDeleting Security Group\n")
except:
	print("\nInstance is Using Security Group, skipping Delete\n")

print("\nTrying to Create Security Group\n")
#Create Security Group
try:
	create_group = client.create_security_group(
		Description='secutiry group da aps 3',
		GroupName=group_name,
		VpcId='vpc-ebd11591'
	)
	#Authorize Security Group (port 22 and 5000)
	auth_group = client.authorize_security_group_ingress(
    GroupName=group_name,
    IpPermissions=[{'IpProtocol': 'tcp', 'FromPort': 5000, 'ToPort': 5000, 'IpRanges':[{'CidrIp': '0.0.0.0/0'}]},{'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    ])
	print("\nSecurity Group Created Successfully\n")
except:
	print("\nCan't Create Security Group, already exists\n")


##USER DATA##
user_data_script = """#!/bin/bash
sudo apt update -y
sudo apt-get install -y python3.6
sudo apt install -y python3-pip
pip3 install flask
pip3 install requests
pip3 install flask_restful
pip3 install pprint
cd home/ubuntu/
git clone https://github.com/SabrinaSimao/Cloud.git
cd Cloud/APS/
chmod +x fortune
python3 fortune.py
"""

tag_node = [
		    {
		        'ResourceType': 'instance',
		        'Tags': [
		            {
		                'Key': 'Owner',
		                'Value': 'Sabrina'
		            },
		        ]
		    },
		]


def launch_instance(ec2, user_data_script, Key_Name, group_name, tag):
	print("\nLaunching Instance: \n")
	#############################
	##     Create Instance    ##
	new_instance = ec2.create_instances(
		ImageId='ami-0ac019f4fcb7cb7e6', 
		MinCount=1, 
		MaxCount=1,
		UserData=user_data_script,
		KeyName=Key_Name,
		InstanceType="t2.micro",
		SecurityGroups=[group_name],	
		TagSpecifications=tag
	)

	print("\nCREATED INSTANCE: \n")
	pprint.pprint(new_instance)


##LAUNCH NODES##
i = 0
while i < size:
	launch_instance(ec2, user_data_script, Key_Name, group_name, tag_node)
	i+=1

#close file just in case
pub_key.close()
