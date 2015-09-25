from fabric import api
from fabric.api import *
from fabric.operations import *


from boto import ec2


import os
from datetime import date


AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "")
DATABASE_URL = os.getenv("STAGING_DATABASE_URL", "")
SECRET_KEY = os.getenv("SECRET_KEY", "")

STAGING_IP = "tf2stats.vokal.io"


def get_git_hash():
    return local("git rev-parse --short HEAD", capture=True)

def staging():
    env.hosts = [STAGING_IP,]
    env.user = "ubuntu"
    env.branch = "master"

def create_image():
    conn = ec2.connect_to_region("us-west-2",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY)

    elastic_ips = conn.get_all_addresses([STAGING_IP,])
    assert len(elastic_ips) == 1

    instance_id = elastic_ips[0].instance_id

    image_id = conn.create_image(instance_id,
            "tf2stats-{0}-{1}".format(date.today().isoformat(),
                get_git_hash()), no_reboot=False)
    print "Created AMI {0}".format(image_id)

def migrate():
    pass

def update():
    require("hosts", provided_by=[staging,])

    with settings(warn_only=True):
        sudo("docker rm $(docker ps -aq)")
        sudo("docker rmi $(docker images --filter dangling=true --quiet)")
        sudo("service tf2stats stop")

    sudo("docker pull docker.vokal.io/tf2stats")

    sudo("service tf2stats start")
    sudo("sleep 5")
    sudo("service nginx-www restart")
