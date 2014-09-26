# Blue Shell brought to you by Isaac Banner, Kyle Brousseau,
#   Nintendo, and The Racer in 8th Place
#
# Alright, lets update some instances
# To begin, you need a credentials file saved in the default boto directory (see Python AWS docs)
#   or you can pass in the key info like so:
#
#      conn = boto.ec2.connect_to_region(availability_zone,
#       ...    aws_access_key_id='<aws access key>',
#       ...    aws_secret_access_key='<aws secret key>')
#
# Once you've got that done, modify availability_zone, key_dir, and keys to the values you need.
#

import subprocess
import boto.ec2

# Availability Zone Goes Here
availability_zone = "us-east-1"

# Where you keep your keys
key_dir = "/Users/isaacbanner/.ssh/"

# Keys you're looking to use
keys = ['at', 'at-chef']


# Utility strings
sshopts = "-o 'StrictHostKeyChecking=no' -o 'UserKnownHostsFile=/dev/null' -o 'ConnectTimeout=10'"
check = "env x=\"() { :;}; echo vulnerable\" bash -c \"echo this is a test\""
cmd = "sudo apt-get update; sudo apt-get --only-upgrade install bash"

# Checks if an update is necessary, then fires the Blue Shell
def main():
    # Connect to EC2 and get all your instances
    ec2 = boto.ec2.connect_to_region(availability_zone)
    reservations = ec2.get_all_reservations()
    for reservation in reservations:
        for instance in reservation.instances:
            # Only execute this stuff on a running machine
            if(instance.state == "running"):
                key = instance.key_name
                ip = instance.private_ip_address
                print(ip + " - " + key)
                if(key in keys):
                    ssh_comm = "ssh -i " + key_dir + key + ".pem " + sshopts + " ubuntu@" + ip 
                    try:
                        v_check = ssh_comm + " '" + check + "'"
                        v_response = subprocess.check_output(v_check, shell=True)
                        if("vulnerable" in v_response):
                            print("\tVulnerable \n\tUpdating now...")
                            update_comm = ssh_comm + " '" + cmd + "'"
                            try:
                                update_response = subprocess.check_output(update_comm, shell = True)
                                v_response = subprocess.check_output(v_check, shell=True)
                                if("vulnerable" not in v_response):
                                    print("\tBlue Shell successfully deployed")
                                else:
                                    print("\tUpdate unsuccessful")
                                break
                            except:
                                print("\tUnable to update")
                        else:
                            print("\tNot vulnerable")
                        break
                    except:
                        print("\tUnable to ssh - error unknown")
                else:
                    print("\tUnable to ssh - need key " + key + ".pem")

main()
