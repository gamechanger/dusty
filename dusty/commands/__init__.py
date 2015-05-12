"""Entrypoint which the daemon uses for processing incoming commands."""

from . import bundle

COMMAND_TREE = {
    'bundle': {
        'list': bundle.list_bundles,
        'activate': bundle.activate_bundle,
        'deactivate': bundle.deactivate_bundle
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
            return 'ERROR: Unexpected argument {}, expected one of: {}'.format(word, ', '.join(tree.keys()))
    return 'ERROR: Unexpected end of command, expected one of: {}'.format(', '.join(tree.keys()))
