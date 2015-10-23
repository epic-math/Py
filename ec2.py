#!/bin/python
import os
import sys
import boto
import boto.ec2
import time

conn = boto.ec2.connect_to_region("us-west-1")

myCode = """#!/bin/bash
sudo mkfs.ext4 /dev/xvdf
sudo mkdir /vol
echo "/dev/xvdf /vol auto noatime 0 0" | sudo tee -a /etc/fstab"""

#### creating a new instance ####
new_reservation = conn.run_instances("ami-d16a8b95",
    key_name="bogo",
    instance_type="t1.micro",
    security_group_ids=["sg-0841236d"],
    user_data=myCode
    )

instance = new_reservation.instances[0]

conn.create_tags([instance.id], {"Name":"bogo-instance"})
while instance.state == u'pending':
    print "Instance state: %s" % instance.state
    time.sleep(10)
    instance.update()

print "Instance state: %s" % instance.state
print "Public dns: %s" % instance.public_dns_name

#### Create a volume ####
# create_volume(size, zone, snapshot=None, volume_type=None, iops=None)
vol = conn.create_volume(10, "us-west-1c")
print 'Volume Id: ', vol.id

# Add a Name tag to the new volume so we can find it.
conn.create_tags([vol.id], {"Name":"bogo-volume"})

# We can check if the volume is now ready and available:
curr_vol = conn.get_all_volumes([vol.id])[0]
while curr_vol.status == 'creating':
      curr_vol = conn.get_all_volumes([vol.id])[0]
      print 'Current Volume Status: ', curr_vol.status
      time.sleep(2)
print 'Current Volume Zone: ', curr_vol.zone


#### Attach a volume ####
result = conn.attach_volume (vol.id, instance.id, "/dev/sdf")
print 'Attach Volume Result: ', result
