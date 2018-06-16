import re
import paramiko
import os, ast
from modules.host import Host
from helpers.logs import logger

config = ast.literal_eval(os.environ.get("CONFIG"))

class SSH(Host):
    def __init__(self, ip, local_ip, port=22, login=None, password=None):
        super(SSH, self).__init__(ip, local_ip, port, login, password)
        # def connect(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname=self.local_ip, port=self.port, username=self.login, password=self.password)

        self.config = config['os_types']['{}'.format(__class__.system_type(self))]
        self.packetSSH = self.config['SSH']['packet']
        self.processSSH = self.config['SSH']['process']
        self.install_command = self.config['packet_manager']
        self.root = SSH.is_user_root(self)

    def run_command(self, cmd, allow_fail=False):
        # if not self.is_pingable:
        #     raise ResourceWarning("Host not available")
        # else:
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
        if stdout:
            result = ""
            for line in stdout:
                result += line
            return result
        else:
            return stderr.readlines()

    def is_user_root(self):
        _test = __class__.run_command(self, "whoami")
        if re.search('root', _test):
            return True
        else:
            return False

    # @property
    def system_type(self):
        _test = __class__.run_command(self, "apt -h")
        if re.search('apt: command not found', _test) or _test == '':
            _test = __class__.run_command(self, "yum -h")
            if re.search("No command 'yam' found", _test) or _test == '':
                return "System is not Debian or Red Hat"
            else:
                return 'centos'
        else:
            return 'ubuntu'

    def reboot_system(self):
        try:
            __class__.run_command(self, "reboot")
        except Exception as e:
            logger.error("Reboot has not been performed. Error '{}' occurred".format(type(e)))

    def check_SSH_service_installation(self):
        test = __class__.run_command(self, "systemctl list-units --type=service --all | grep {}".format(self.processSSH))
        if re.search('{}'.format(self.processSSH), test):
            return True
        else:
            return False

    @property
    def is_SSH_installed(self):
        return SSH.check_SSH_service_installation(self)

    def check_SSH_service_status(self):
        test = __class__.run_command(self, "systemctl status {}".format(self.processSSH))
        if re.search("Active: active", test):
            return True
        else:
            return False

    @property
    def is_SSH_active(self):
        return SSH.check_SSH_service_status(self)

    def install_SSH_service(self):
        try:
            SSH.run_command(self, "{} install {}".format(self.install_command, self.packetSSH))
            SSH.run_command(self, self.password + '\n')
        except Exception as e:
            print("Install SSH service. Error '{}' occurred".format(type(e)))

    def service_SSH_action(self, cmd): #use 'start', 'restart' or 'stop'  as cmd
        self.cmd = cmd
        try:
            SSH.run_command(self, "systemctl {} {}".format(cmd, self.processSSH))
            SSH.run_command(self, self.password)
        except Exception as e:
            ("SSH service action. Error '{}' occurred".format(type(e)))

    @property
    def is_SSH_key_pair_exist(self):
        test = SSH.run_command(self, '[ -f .ssh/id_rsa.pub ] && echo "Found" || echo "Not found"')
        if test == "Found\n":
            return True
        else:
            return False

    def SSH_key_pair(self):
        if self.is_SSH_key_pair_exist == False:
            k = paramiko.RSAKey.generate(bits=1024)
            SSH.run_command(self, "echo '{}' >> .ssh/id_rsa.pub".format(k))
        self.ssh_key = __class__.run_command(self, "cat ~/.ssh/id_rsa.pub")
        return self.ssh_key

    def copy_SSH_key(self, key):
        self.key = key
        try:
            SSH.run_command(self, "echo '{}' >> .ssh/authorized_keys".format(key))
        except Exception as e:
            logger.error("Copy SSH key. Error '{}' occurred".format(type(e)))

    def logs(self):
        try:
            paramiko.util.log_to_file('log_file.txt')
        except Exception as e:
            logger.error("Logs. Error '{}' occurred".format(type(e)))

    def close_SSH(self):
        return self.ssh_client.close()