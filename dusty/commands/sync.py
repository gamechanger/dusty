from ..compiler.spec_assembler import get_all_repos
from ..systems.rsync import sync_repos as perform_sync_repos
from ..source import Repo
from ..payload import daemon_command

@daemon_command
def sync_repos(*repos):
    all_repos = get_all_repos(active_only=True, include_specs_repo=False)
    if not repos:
        repos = all_repos
    else:
        repo_objects = [Repo.resolve(all_repos, repo_name) for repo_name in repos]
        repos = repo_objects
    perform_sync_repos(set(repos))
