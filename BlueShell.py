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
# Also, make sure the permissions on your key files are all 600. Otherwise this wont work and it's
#   not our fault. No excuses.
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
    # Maintain a list of all instances potentially still insecure at the end of the run.
    red_shells = []
    
    # Connect to EC2 and get all your instances
    ec2 = boto.ec2.connect_to_region(availability_zone)
    reservations = ec2.get_all_reservations()
    for reservation in reservations:
        for instance in reservation.instances:
            # Only execute this stuff on a running machine
            if(instance.state == "running"):
                key = instance.key_name
                ip = instance.private_ip_address
                try:
                    print(ip + " - " + key)
                except:
                    print("Unable to print ip/key pair - Likely issue is a non-unicode key name")
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
                                    red_shells.append(ip + " - insecure")
                                    print("\tUpdate unsuccessful")
                            except:
                                red_shells.append(ip + " - insecure")
                                print("\tUnable to update")
                        else:
                            print("\tNot vulnerable")
                        break
                    except:
                        red_shells.append(ip + " - unreachable")
                        print("\tUnable to ssh - error unknown, please see python/console logs for more info")
                else:
                    red_shells.append(ip + " - unreachable")
                    try:
                        print("\tUnable to ssh - need key " + key + ".pem")
                    except:
                        print("\tUnable to ssh - need key. Also, we can't read your non-unicode keys. Stop.")

    print("Unresolved Instances: ")
    for shell in red_shells:
        print(shell)

main()

