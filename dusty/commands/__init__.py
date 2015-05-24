"""Entrypoint which the daemon uses for processing incoming commands."""

from . import bundles, repos, sync, manage_config, run
from .. import compiler

COMMAND_TREE = {
    'bundles': {
        'list': bundles.list_bundles,
        'activate': bundles.activate_bundle,
        'deactivate': bundles.deactivate_bundle
    },
    'repos': {
        'list': repos.list_repos,
        'override': repos.override_repo,
        'manage': repos.manage_repo,
        'from': repos.override_repos_from_directory,
        'update': repos.update_managed_repos
    },
    'sync': sync.sync_repos,
    'config': {
        'list': manage_config.list_config,
        'listvalues': manage_config.list_config_values,
        'set': manage_config.save_value
    },
    'up': run.start_local_env,
    'stop': run.stop_local_env
}

def process_command(command_string):
    tree = COMMAND_TREE
    words = [word.strip() for word in command_string.split(' ')]
    while words:
        word = words.pop(0)
        if word in tree:
            if callable(tree[word]):
                return tree[word](*words)
            else:
                tree = tree[word]
                continue
        else:
            raise ValueError('Unexpected argument {}, expected one of: {}'.format(word, ', '.join(tree.keys())))
    raise ValueError('Unexpected end of command, expected one of: {}'.format(', '.join(tree.keys())))
