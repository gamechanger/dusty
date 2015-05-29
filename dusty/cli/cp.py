"""Copy files between your local filesystem and Dusty-managed containers.
This tool also supports copying files directly between two containers.

To specify a file or directory location, either give just a path to
indicate a location on your local filesystem, or prefix a path with
`<service>:` to indicate a location inside a running container.

Usage:
  cp <source> <destination>

Examples:
  To copy a file from your local filesystem to the container of an app called `website`:
    cp /tmp/my-local-file.txt website:/tmp/file-inside-website-container.txt

  To copy a file from that same `website` container back to your local filesystem:
    cp website:/tmp/file-inside-website-container.txt /tmp/my-local-file.txt

  To copy a file from the `website` container to a different container called `api`:
    cp website:/tmp/website-file.txt api:/different/location/api-file.txt
"""

from docopt import docopt

from ..payload import Payload
from ..commands.cp import copy_between_containers, copy_from_local, copy_to_local

def _split_path(path):
    split = path.split(':')
    if len(split) > 2:
        raise ValueError('Invalid path specification, expected [container:]path.')
    elif len(split) == 2:
        return split[0], split[1]
    return None, path

def main(argv):
    args = docopt(__doc__, argv)
    source_name, source_path = _split_path(args['<source>'])
    dest_name, dest_path = _split_path(args['<destination>'])
    if source_name and dest_name:
        return Payload(copy_between_containers, source_name, source_path, dest_name, dest_path)
    elif dest_name:
        return Payload(copy_from_local, source_path, dest_name, dest_path)
    elif source_name:
        return Payload(copy_to_local, dest_path, source_name, source_path)
    else:
        raise ValueError('Refusing to copy files between your local filesystem.')
