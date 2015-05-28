"""Basic tools for managing disk usage in the boot2docker VM
Usage:
  disk inspect
  disk cleanup_containers
  disk cleanup_images

Commands:
  inspect             Prints VM disk usage information
  cleanup_containers  Cleans docker containers that have exited
  cleanup_images      Removes docker images that can be removed without the --force flag
"""

from docopt import docopt

from ..payload import Payload
from ..commands.disk import inspect_vm_disk, cleanup_inactive_containers, cleanup_images

def main(argv):
    args = docopt(__doc__, argv)
    if args['inspect']:
        return Payload(inspect_vm_disk)
    elif args['cleanup_containers']:
        return Payload(cleanup_inactive_containers)
    elif args['cleanup_images']:
        return Payload(cleanup_images)
