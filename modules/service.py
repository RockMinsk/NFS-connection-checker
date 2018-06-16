import re
from modules.ssh import SSH


class Service(SSH):
    def __init__(self, ip, local_ip, port=None, login=None, password=None):
        super(Service, self).__init__(ip, local_ip, port, login, password)
        self.packet = None
        self.process = None

    def check_service_installation(self):
        test = __class__.run_command(self, "systemctl list-units --type=service --all | grep {}".format(self.process))
        if re.search('{}'.format(self.process), test):
            return True
        else:
            return False

    def check_service_status(self):
        test = __class__.run_command(self, "systemctl status {}".format(self.process))
        if re.search("Active: active", test):
            return True
        else:
            return False

    def install_service(self):
        try:
            __class__.run_command(self, "{} install {}".format(self.install_command, self.packet))
            __class__.run_command(self, self.password + '\n')
        except Exception as e:
            print("Install {} service. Error '{}' occurred".format(__class__.__name__, type(e)))

    def service_action(self, cmd):  # use 'start', 'restart' or 'stop'  as cmd
        self.cmd = cmd
        try:
            __class__.run_command(self, "systemctl {} {}".format(cmd, self.process))
        except Exception as e:
            print("{}. Error '{}' occurred".format(__class__.install_service.__name__, type(e)))
