def ssh_check(host):
    if host.is_SSH_installed == False:
        host.install_SSH_service()
    if host.is_SSH_active == False:
        host.service_SSH_action('start')