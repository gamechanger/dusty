"""Functions with operate on the Docker client's config file"""

import os
import json
from urlparse import urlparse
import getpass
from subprocess import CalledProcessError

from ... import constants
from ...log import log_to_client
from ...memoize import memoized
from ...subprocess import check_call_demoted

def registry_from_image(image_name):
    """Returns the Docker registry host associated with
    a given image name."""
    if '/' not in image_name: # official image
        return constants.PUBLIC_DOCKER_REGISTRY
    prefix = image_name.split('/')[0]
    if '.' not in prefix: # user image on official repository, e.g. thieman/clojure
        return constants.PUBLIC_DOCKER_REGISTRY
    return prefix # custom registry, e.g. gamechanger.io/lox

@memoized
def get_authed_registries():
    """Reads the local Docker client config for the current user
    and returns all registries to which the user may be logged in.
    This is intended to be run client-side, not by the daemon."""
    result = set()
    if not os.path.exists(constants.DOCKER_CONFIG_PATH):
        return result
    config = json.load(open(constants.DOCKER_CONFIG_PATH, 'r'))
    for registry in config.get('auths', {}).iterkeys():
        try:
            parsed = urlparse(registry)
        except Exception:
            log_to_client('Error parsing registry {} from Docker config, will skip this registry').format(registry)
        # This logic assumes the auth is either of the form
        # gamechanger.io (no scheme, no path after host) or
        # of the form https://index.docker.io/v1/ (scheme,
        # netloc parses correctly, additional path does not matter).
        # These are the formats I saw in my personal config file,
        # not sure what other formats it might accept.
        result.add(parsed.netloc) if parsed.netloc else result.add(parsed.path)
    return result

def log_in_to_registry(registry):
    log_to_client('\nProcessing required login for {}'.format(registry))

    while True:
        username = raw_input('Username: ')
        password = getpass.getpass('Password: ')
        email = raw_input('Email: ')

        args = ['-u', username,
                '-p', password,
                '-e', email]
        if registry != constants.PUBLIC_DOCKER_REGISTRY:
            args.append(registry)

        try:
            check_call_demoted(['docker', 'login'] + args)
        except CalledProcessError:
            log_to_client('\nLogin failed, please try again for {} (Ctrl-C to quit)\n'.format(registry))
        else:
            break

    log_to_client('Login successful for {}'.format(registry))
