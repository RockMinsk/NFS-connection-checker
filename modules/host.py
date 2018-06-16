import os, platform

class Host(object):
    def __init__(self, ip, local_ip, port=None, login=None, password=None):
        self.ip = ip
        self.local_ip = local_ip
        self.port = port
        self.login = login
        self.password = password

    @property
    def is_pingable(self):
        test = os.system("ping " + ("-n 1 " if platform.system().lower() == "windows" else "-c 1 ") + self.ip)
        if test == 0:
            return True
        else:
            return False