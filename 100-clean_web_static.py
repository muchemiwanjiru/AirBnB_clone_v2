#!/usr/bin/python3
"""
deployment module for fabric
"""

from fabric.api import local, env, put, run, cd, lcd
from datetime import datetime
from os import path, listdir
from fabric.decorators import runs_once


env.hosts = ['100.25.164.140', '54.152.190.234']

# Set the username
env.user = "ubuntu"

# Set private key path
env.key_filename = "~/.ssh/id_rsa"


@runs_once
def do_pack():
    """ generates a .tgz archive from the contents of
    the web_static folder of your AirBnB Clone repo
    """

    local("mkdir -p versions")
    date_format = "%Y%m%d%H%M%S"
    archive_path = "versions/web_static_{}.tgz".format(
            datetime.strftime(datetime.now(), date_format))
    result = local("tar -cvzf {} web_static".format(archive_path))
    if result.failed:
        return None
    return archive_path


def do_deploy(archive_path):
    """distributes an archive to your web servers"""

    try:
        if not path.exists(archive_path):
            return False

        dir_path = "/data/web_static/releases/"
        filename = path.basename(archive_path)
        file_no_ext, ext = path.splitext(filename)
        put(archive_path, "/tmp/{}".format(filename))
        run("rm -rf {}{}".format(dir_path, file_no_ext))
        run("mkdir -p {}{}".format(dir_path, file_no_ext))
        run("tar -xzf /tmp/{} -C {}{}".format(filename, dir_path, file_no_ext))
        run("rm /tmp/{}".format(filename))
        run("mv {0}{1}/web_static/* {0}{1}/".format(dir_path, file_no_ext))
        run("rm -rf {}{}/web_static".format(dir_path, file_no_ext))
        run("rm -rf /data/web_static/current")
        run("ln -s {}{}/ /data/web_static/current".format(
            dir_path, file_no_ext))
        print("New version deployed!")
        return True
    except Exception:
        return False


def deploy():
    """creates and distributes an archive to your web servers"""
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)


def do_clean(number=0):
    """deleting the out-of-date archives"""
    nbr = 2 if int(number) == 0 else int(number) + 1

    with lcd("versions"):
        local("ls -dt * | tail -n +{} | sudo xargs rm -f".format(nbr))
    with cd("/data/web_static/releases"):
        run("ls -dt * | tail -n +{} | sudo xargs rm -rf".format(nbr))
