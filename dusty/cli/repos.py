"""Manage repos referenced in the current Dusty specs.

By default, Dusty automatically manages the repos referenced
in your app and lib specs. This includes cloning the repo and
pulling updates from master to keep the Dusty-managed copy up-to-date.

Alternatively, you can override a repo to manage it yourself. This
is useful for actively developing apps and libs that depend on that
repo. To override a repo, use the `override` or `from` commands.

Usage:
  repos from <source_path>
  repos list
  repos manage (--all | <repo_name>)
  repos override <repo_name> <source_path>
  repos update

Commands:
  from        Override all repos from a given directory
  list        Show state of all repos referenced in specs
  manage      Tell Dusty to manage a repo or all repos, removing any overrides
  override    Override a repo with a local copy that you manage
  update      Pull latest master on Dusty-managed repos

Options:
  --all       When provided to manage, dusty will manage all currently overridden repos
"""

from docopt import docopt

from ..payload import Payload
from ..commands.repos import (list_repos, override_repo, manage_repo, manage_all_repos,
                              override_repos_from_directory, update_managed_repos)

def main(argv):
    args = docopt(__doc__, argv)
    if args['list']:
        return Payload(list_repos)
    elif args['override']:
        return Payload(override_repo, args['<repo_name>'], args['<source_path>'])
    elif args['manage']:
        if args['--all']:
            return Payload(manage_all_repos)
        else:
            return Payload(manage_repo, args['<repo_name>'])
    elif args['from']:
        return Payload(override_repos_from_directory, args['<source_path>'])
    elif args['update']:
        return Payload(update_managed_repos)
