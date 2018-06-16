import unittest
import re
from main import nfs_server, nfs_client
from helpers.logs import logger

class TestClientRights_777_ReadWrite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger.info("Start {}".format(__class__.__name__))

    def setUp(self):
        nfs_server.create_folder()
        logger.info("Folder '{}' has created".format(nfs_server.shared_folder))
        nfs_server.set_rights_to_shared_folder('777') # full rights
        nfs_server.export_shared_folder('rw,sync')
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

    def test_RW_client_can_create_folder(self):
        logger.info("Start 'test_RW_client_can_create_folder'")
        nfs_client.create_folder()
        self.assertTrue(nfs_server.is_folder_created)

    def test_RW_client_can_create_files(self):
        logger.info("Start 'test_RW_client_can_create_files'")
        nfs_client.create_file()
        self.assertTrue(nfs_server.is_file_created)

    def test_RW_client_can_read_files(self):
        logger.info("Start 'test_RW_client_can_read_files'")
        nfs_server.create_file()
        nfs_server.modify_file()
        self.assertEqual(nfs_client.open_modified_file(), nfs_server.open_modified_file())

    def test_RW_client_can_modify_files(self):
        logger.info("Start 'test_RW_client_can_modify_files'")
        nfs_server.create_file()
        nfs_client.modify_file()
        _test_server_hash = re.match(r"(^\S*)", nfs_server.file_hash())
        _test_client_hash = re.match(r"(^\S*)", nfs_client.file_hash())
        self.assertEqual(_test_server_hash.group(0), _test_client_hash.group(0))

    def test_RW_client_can_delete_folder(self):
        logger.info("Start 'test_RW_client_can_modify_files'")
        nfs_client.delete_folder()
        self.assertFalse(nfs_server.is_folder_created)

    def test_RW_client_can_delete_files_created_on_server_side(self):
        logger.info("Start 'test_RW_client_can_delete_files_created_on_server_side'")
        nfs_server.create_file()
        nfs_server.set_file_permissions('777')
        nfs_server.service_action('restart')
        nfs_client.delete_file()
        self.assertFalse(nfs_server.is_file_created)

    def test_RW_client_can_delete_files_created_by_himself(self):
        logger.info("Start 'test_RW_client_can_delete_files_created_by_himself'")
        nfs_client.create_file()
        nfs_client.delete_file()
        self.assertFalse(nfs_server.is_file_created)

def suite2():
    suite = unittest.TestSuite()
    suite.addTest(TestClientRights_777_ReadWrite('test_RW_client_can_create_folder'))
    suite.addTest(TestClientRights_777_ReadWrite('test_RW_client_can_create_files'))
    suite.addTest(TestClientRights_777_ReadWrite('test_RW_client_can_read_files'))
    suite.addTest(TestClientRights_777_ReadWrite('test_RW_client_can_modify_files'))
    suite.addTest(TestClientRights_777_ReadWrite('test_RW_client_can_delete_folder'))
    suite.addTest(TestClientRights_777_ReadWrite('test_RW_client_can_delete_files_created_on_server_side'))
    suite.addTest(TestClientRights_777_ReadWrite('test_RW_client_can_delete_files_created_by_himself'))
    return suite