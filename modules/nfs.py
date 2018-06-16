import string, random
import os, ast
from modules.service import Service
from helpers.logs import logger

config = ast.literal_eval(os.environ.get("CONFIG"))


class NFS(Service):
    def __init__(self, ip, local_ip, port, login=None, password=None):
        super(NFS, self).__init__(ip, local_ip, port, login, password)
        self.process = self.config['NFS']['process']
        self.shared_folder = None
        self.shared_file = None
        self.text = None
        self.path_to_folder = None
        self.path_to_file = None

    @property
    def is_NFS_installed(self):
        return NFS.check_service_installation(self)

    @property
    def is_NFS_active(self):
        return NFS.check_service_status(self)

    def create_folder(self):
        try:
            _folder = ''.join(random.choice(string.ascii_letters) for _ in range(10))
            self.shared_folder = _folder
            os.environ["SHARED_FOLDER"] = self.shared_folder
            NFS.run_command(self, "mkdir {}".format(self.path_to_folder))
        except Exception as e:
            logger.error("Create folder. Error '{}' occurred".format(type(e)))

    def set_rights_to_shared_folder(self, permissions):  # enter necessary permissions, e.g. '777'
        try:
            NFS.run_command(self, "chmod {} {}".format(permissions, self.path_to_folder))
        except Exception as e:
            logger.error("Set rights to shared folder. Error '{}' occurred".format(type(e)))

    @property
    def is_folder_created(self):
        test = NFS.run_command(self, '[ -d {} ] && echo "Found" || echo "Not found"'.format(self.path_to_folder))
        if test == "Found\n":
            return True
        else:
            return False

    def delete_folder(self):
        try:
            NFS.run_command(self, "rm -rf {}".format(self.path_to_folder))
        except Exception as e:
            logger.error("Delete folder. Error '{}' occurred".format(type(e)))

    def create_file(self):
        try:
            _file = ''.join(random.choice(string.ascii_letters) for _ in range(10))
            self.shared_file = _file
            os.environ["SHARED_FILE"] = self.shared_file
            NFS.run_command(self, "touch {}".format(self.path_to_file))
        except Exception as e:
            logger.error("Create file. Error '{}' occurred".format(type(e)))

    def set_file_permissions(self, permissions):  # enter necessary permissions, e.g. '777'
        try:
            NFS.run_command(self, "chmod {} {}".format(permissions, self.path_to_file))
        except Exception as e:
            logger.error("Set file permissions. Error '{}' occurred".format(type(e)))

    def modify_file(self):
        try:
            self.text = ''.join(random.choice(string.ascii_letters) for _ in range(100))
            NFS.run_command(self, "echo '{}' >> {}".format(self.text, self.path_to_file))
        except Exception as e:
            logger.error("Modify file. Error '{}' occurred".format(type(e)))

    def open_modified_file(self):
        try:
            NFS.run_command(self, "cat {}".format(self.path_to_file))
        except Exception as e:
            logger.error("Open modified file. Error '{}' occurred".format(type(e)))

    def delete_file(self):
        try:
            NFS.run_command(self, "rm -rf {}".format(self.path_to_file))
        except Exception as e:
            logger.error("Delete file. Error '{}' occurred".format(type(e)))

    @property
    def is_file_created(self):
        test = NFS.run_command(self, "ls {} | grep -w {}".format(self.path_to_folder, self.shared_file))
        if test == self.shared_file:
            return True
        else:
            return False

    def file_hash(self):
        try:
            NFS.run_command(self, "sha1sum {}".format(self.path_to_file))
        except Exception as e:
            logger.error("File hash. Error '{}' occurred".format(type(e)))


class ServerNFS(NFS):
    def __init__(self, ip, local_ip, port, login=None, password=None):
        super(ServerNFS, self).__init__(ip, local_ip, port, login, password)
        self.packet = self.config['NFS']['packet']['server']
        self.shared_folder = os.environ.get("SHARED_FOLDER")
        self.shared_file = os.environ.get("SHARED_FILE")
        self.path_to_folder = "/var/nfsshare/{}".format(self.shared_folder)
        self.path_to_file = "/var/nfsshare/{}/{}".format(self.shared_folder, self.shared_file)

    def export_shared_folder(self, cmd):  # enter rights commands, e.g. 'rw' or 'all_squash'
        try:
            NFS.run_command(self, "echo '{} {}({})' > /etc/exports"
                            .format(self.path_to_folder, config['hosts']['clients']['ip'], cmd))
        except Exception as e:
            logger.error("Export shared folder. Error '{}' occurred".format(type(e)))

    def remove_file_exports(self):
        try:
            NFS.run_command(self, "rm -rf /etc/exports".format(self.password))
        except Exception as e:
            logger.error("File 'Exports' has not been removed. Error '{}' occurred".format(type(e)))


class ClientNFS(NFS):
    def __init__(self, ip, local_ip, port, login=None, password=None):
        super(ClientNFS, self).__init__(ip, local_ip, port, login, password)
        self.packet = self.config['NFS']['packet']['client']

    def mount_shared_folders(self):
        try:
            self.shared_folder = os.environ.get("SHARED_FOLDER")
            self.shared_file = os.environ.get("SHARED_FILE")
            self.path_to_folder = "/mnt/nfs/var/nfsshare/{}".format(self.shared_folder)
            self.path_to_file = "/mnt/nfs/var/nfsshare/{}/{}".format(self.shared_folder, self.shared_file)
            NFS.run_command(self, "mount {}:/var/nfsshare/{} {}"
                            .format(config['hosts']['server']['ip'],
                                    self.shared_folder, self.path_to_folder))
        except Exception as e:
            logger.error("Mount shared folder. Error '{}' occurred".format(type(e)))
