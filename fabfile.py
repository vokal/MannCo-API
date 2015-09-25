from fabric import api
from fabric.api import *
from fabric.operations import *


STAGING_IP = "tf2stats.vokal.io"


def staging():
    env.hosts = [STAGING_IP,]
    env.user = "ubuntu"
    env.branch = "master"

def update():
    require("hosts", provided_by=[staging,])

    with settings(warn_only=True):
        sudo("docker rm $(docker ps -aq)")
        sudo("docker rmi $(docker images --filter dangling=true --quiet)")
        sudo("service tf2stats stop")

    sudo("docker pull docker.vokal.io/tf2stats")

    sudo("service tf2stats start")
