"""Basic tools for managing disk usage in the boot2docker VM

Usage:
  disk inspect
  disk cleanup_containers
  disk cleanup_images
  disk backup <destination-path>
  disk restore <source-path>

Commands:
  inspect             Prints VM disk usage information
  cleanup_containers  Cleans docker containers that have exited
  cleanup_images      Removes docker images that can be removed without the --force flag
  backup              Backs up the /persist directory on your boot2docker to your local file system
  restore             Restores a backed up /persist directory
"""

from docopt import docopt

from ..payload import Payload
from ..commands.disk import (inspect_vm_disk, cleanup_inactive_containers, cleanup_images,
                             backup, restore)

def main(argv):
    args = docopt(__doc__, argv)
    if args['inspect']:
        return Payload(inspect_vm_disk)
    elif args['cleanup_containers']:
        return Payload(cleanup_inactive_containers)
    elif args['cleanup_images']:
        return Payload(cleanup_images)
    elif args['backup']:
        return Payload(backup, args['<destination-path>'])
    elif args['restore']:
        return Payload(restore, args['<source-path>'])
