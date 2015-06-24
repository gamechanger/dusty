"""Basic tools for managing disk usage in the boot2docker VM

Usage:
  disk inspect
  disk cleanup_containers
  disk cleanup_images
  disk backup <destination>
  disk restore <source>

Commands:
  inspect             Prints VM disk usage information
  cleanup_containers  Cleans docker containers that have exited
  cleanup_images      Removes docker images that can be removed without the --force flag
  backup              Backs up the /persist directory on your boot2docker to your local file system
  restore             Restores a backed up /persist directory
"""

from docopt import docopt
import os

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
        path = os.path.abspath(args['<destination>'])
        return Payload(backup, path)
    elif args['restore']:
        path = os.path.abspath(args['<source>'])
        print "Warning: this will overwrite the /persist directory on your VM with the contents of {}".format(path)
        if raw_input("Continue? (y/n) ").strip().upper() == 'Y':
            return Payload(restore, path)
        else:
            print "Restore cancelled"
