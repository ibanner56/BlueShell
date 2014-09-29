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
# Also, don't do anything stupid with this script. If you break something, it's also not our fault -
#   you're just dumb.
#

import subprocess
import boto.ec2

# Availability Zone Goes Here
availability_zone = "us-east-1"

# Where you keep your keys
key_dir = "/Users/isaacbanner/.ssh/"

# Keys you're looking to use
keys = ['at', 'at-chef', 'eddie_enernoc_ec2', 'mvp-mesos']
# For use if the instance's key is unavailable
default_key = "at-chef"


# Utility strings
sshopts = "-o 'StrictHostKeyChecking=no' -o 'UserKnownHostsFile=/dev/null' -o 'ConnectTimeout=10'"
check = "env x=\"() { :;}; echo vulnerable\" bash -c \"echo this is a test\""
cmd = "sudo apt-get update; sudo apt-get --only-upgrade install bash"

# Checks if an update is necessary, then fires the Blue Shell
def main():
    # Maintain a list of all instances that were unreachable do to unknown reasons.
    red_shells = []
    
    # Maintain a list of all instances we couldn't access due to key issues (e.g. not having the key)
    bananas = []
    
    # Maintain a list of all instances that didn't pass the check after running the update
    poison_mushrooms = []       # It was in Super Mario Kart. It's canon.
    
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
                    print("Unable to print ip/key pair - Likely cause is aws isn't providing a key name")
                if(key in keys or key == None):
                    # Children, do NOT try this at home. I'm a professional. I swear.
                    if(key == None):
                        # This is to deal with the fact that a large portion of our autoscale groups
                        # Use at-chef, but don't have it listed in AWS...
                        print("Attempting to use " + ip + " - " + default_key)
                        key = default_key
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
                                    poison_mushrooms.append(ip + " - insecure post update")
                                    print("\tUpdate unsuccessful")
                            except:
                                poison_mushrooms.append(ip + " - unable to confirm update")
                                print("\tUnable to update")
                        else:
                            print("\tNot vulnerable")
                        break
                    except:
                        red_shells.append(ip + " - unreachable")
                        print("\tUnable to ssh - error unknown, please see python/console logs for more info")
                else:
                    try:
                        print("\tUnable to ssh - need key " + key + ".pem")
                        bananas.append(ip + " - don't have key " + key)
                    except:
                        print("\tUnable to ssh - Ccn't get key name.")
                        bananas.append(ip + " - key name unavailable")

    # Print out the data on any instances we didn't confirm as secure.
    print("\nMissing Keys: ")
    for banana in bananas:
        print(banana)
    print("\nStill Insecure Instances: ")
    for mushroom in poison_mushrooms:
        print(mushroom)
    print("\nUnreachable Instances: ")
    for shell in red_shells:
        print(shell)

main()

