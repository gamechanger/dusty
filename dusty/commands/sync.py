from ..compiler.spec_assembler import get_all_repos
from ..systems.rsync import sync_repos as perform_sync_repos

def sync_repos(*repos):
    if not repos:
        repos = get_all_repos(active_only=True, include_specs_repo=False)
    perform_sync_repos(set(repos))
    yield 'Finished sync'
