from . import client
from . import server

def configure_nfs():
    server.configure_nfs_server()
    # client.mount_active_repos()

def update_nfs_with_repos(repos):
    pass
    # server.add_exports_for_repos(repos)
    # client.remount_repos(repos)
