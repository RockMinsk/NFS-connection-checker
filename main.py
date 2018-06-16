import yaml
import unittest
import os, ast
from helpers.ssh_checker import ssh_check
from helpers.nfs_checker import nfs_check

CONFIG_FILE = 'config/configuration.yml'

f = open(CONFIG_FILE, 'r')
config = yaml.load(f)

os.environ["CONFIG"] = str(config)

from modules import nfs

class LocalServerNFS(nfs.ServerNFS):
    def __init__(self, ip, local_ip, port, login, password):
        super(LocalServerNFS, self).__init__(ip, local_ip, port, login, password)

class LocalClientNFS(nfs.ClientNFS):
    def __init__(self, ip, local_ip, port, login, password):
        super(LocalClientNFS, self).__init__(ip, local_ip, port, login, password)

nfs_server = LocalServerNFS(ip=config['hosts']['server']['ip'],
                            local_ip=config['hosts']['server']['local_ip'],
                             port=config['hosts']['server']['SSH_port'],
                             login=config['hosts']['server']['credentials']['login'],
                             password=config['hosts']['server']['credentials']['password'])

nfs_client = LocalClientNFS(ip=config['hosts']['clients']['ip'],
                            local_ip=config['hosts']['clients']['local_ip'],
                             port=config['hosts']['clients']['SSH_port'],
                            login=config['hosts']['clients']['credentials']['login'],
                            password=config['hosts']['clients']['credentials']['password'])

if __name__ == '__main__':
    from tests.testRO import suite1
    from tests.testRW import suite2
    # run SSH and NFS services
    ssh_check(nfs_server)
    ssh_check(nfs_client)
    nfs_check(nfs_server)
    nfs_check(nfs_client)
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite1())
    runner.run(suite2())
    # close SSH connection
    nfs_client.close_SSH()
    nfs_server.close_SSH()