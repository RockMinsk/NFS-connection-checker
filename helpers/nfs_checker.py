def nfs_check(host):
    if host.is_NFS_installed == False:
        host.install_service()
    if host.is_NFS_active == False:
        host.service_action('start')