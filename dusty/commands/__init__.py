"""Entrypoint which the daemon uses for processing incoming commands."""

from . import bundle, repos, manage_config
from .. import compiler

COMMAND_TREE = {
    'bundle': {
        'list': bundle.list_bundles,
        'activate': bundle.activate_bundle,
        'deactivate': bundle.deactivate_bundle
    },
    'repos': {
        'list': repos.list_repos,
        'override': repos.override_repo,
        'manage': repos.manage_repo,
        'from': repos.override_repos_from_directory,
        'update': repos.update_managed_repos
    },
    'compiler': {
        'list': compiler.list_processed_specs
    },
    'config': {
        'list': manage_config.list_config,
        'set': manage_config.set_value
    }
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
