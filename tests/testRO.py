import unittest
import re
from helpers.logs import logger
from main import nfs_server, nfs_client

print(nfs_server.ip, nfs_server.password)
# nfs_server = main.LocalServerNFS()
# nfs_client = main.LocalClientNFS()

class TestClientRights_777_ReadOnly(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger.info("Start {}".format(__class__.__name__))

    def setUp(self):
        nfs_server.create_folder()
        logger.info("Folder '{}' has created".format(nfs_server.shared_folder))
        nfs_server.set_rights_to_shared_folder('777') # full rights
        nfs_server.export_shared_folder('ro,sync')
        logger.info("Folder '{}' has shared".format(nfs_server.shared_folder))
        nfs_server.service_action('restart')
        nfs_client.mount_shared_folders()
        logger.info("Folder '{}' has mounted".format(nfs_client.shared_folder))

    def tearDown(self):
        nfs_server.delete_folder()
        logger.info("Folder '{}' has deleted".format(nfs_server.shared_folder))
        nfs_server.service_action('restart')
        logger.info("Restart of the nfs-server")

    @classmethod
    def tearDownClass(cls):
        logger.info("Finish {}".format(__class__.__name__))

    def test_RO_client_cannot_create_folder(self):
        logger.info("Start 'test_RO_client_cannot_create_folder'")
        _test = nfs_client.create_folder()
        self.assertTrue(re.search(r"mkdir: cannot create directory", _test))

    def test_RO_client_cannot_create_files(self):
        logger.info("Start 'test_RO_client_cannot_create_files'")
        _test = nfs_client.create_file()
        self.assertTrue(re.search(r"touch: cannot touch", _test))

    def test_RO_client_can_read_files(self):
        logger.info("Start 'test_RO_client_can_read_files'")
        nfs_server.create_file()
        nfs_server.modify_file()
        self.assertEqual(nfs_client.open_modified_file(), nfs_server.open_modified_file())

    def test_RO_client_cannot_modify_files(self):
        logger.info("Start 'test_RO_client_cannot_modify_files'")
        nfs_server.create_file()
        _test = nfs_client.modify_file()
        self.assertTrue(re.search(r"Can't open file for writing", _test))

    def test_RO_client_cannot_delete_folder(self):
        logger.info("Start 'test_RO_client_cannot_delete_folder'")
        _test = nfs_client.delete_folder()
        self.assertTrue(re.search(r"rm: cannot remove", _test))

    def test_RO_client_cannot_delete_files(self):
        logger.info("Start 'test_RO_client_cannot_delete_files'")
        nfs_server.create_file()
        nfs_server.set_file_permissions('777')
        nfs_server.service_action('restart')
        _test = nfs_client.delete_file()
        self.assertTrue(re.search(r"rm: cannot remove", _test))

def suite1():
    suite = unittest.TestSuite()
    suite.addTest(TestClientRights_777_ReadOnly('test_RO_client_cannot_create_folder'))
    suite.addTest(TestClientRights_777_ReadOnly('test_RO_client_cannot_create_files'))
    suite.addTest(TestClientRights_777_ReadOnly('test_RO_client_can_read_files'))
    suite.addTest(TestClientRights_777_ReadOnly('test_RO_client_cannot_modify_files'))
    suite.addTest(TestClientRights_777_ReadOnly('test_RO_client_cannot_delete_folder'))
    suite.addTest(TestClientRights_777_ReadOnly('test_RO_client_cannot_delete_files'))
    return suite