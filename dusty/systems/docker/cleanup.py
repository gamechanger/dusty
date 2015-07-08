import logging

from ...log import log_to_client
from . import get_dusty_containers_with_client, get_dusty_images, get_docker_client

def get_exited_dusty_containers(client):
    all_containers = get_dusty_containers_with_client(client, None, include_exited=True)
    stopped_containers = []
    for container in all_containers:
        if 'Exited' in container['Status']:
            stopped_containers.append(container)
    return stopped_containers

def remove_exited_dusty_containers():
    """Removed all dusty containers with 'Exited' in their status"""
    client = get_docker_client()
    exited_containers = get_exited_dusty_containers(client)
    removed_containers = []
    for container in exited_containers:
        log_to_client("Removing container {}".format(container['Names'][0]))
        try:
            client.remove_container(container['Id'])
            removed_containers.append(container)
        except Exception as e:
            log_to_client(e.message or str(e))
    return removed_containers

def _remove_dangling_images(client):
    dangling_images = client.images(all=True, filters={'dangling': True})
    removed = []
    for image in dangling_images:
        try:
            client.remove_image(image['Id'])
        except Exception as e:
            logging.info("Couldn't remove image {}".format(image['RepoTags']))
        else:
            log_to_client("Removed Image {}".format(image['RepoTags']))
            removed.append(image)
    return removed

def remove_images():
    """Removes all dangling images as well as all images referenced in a dusty spec; forceful removal is not used"""
    client = get_docker_client()
    removed = _remove_dangling_images(client)
    dusty_images = get_dusty_images()
    all_images = client.images(all=True)
    for image in all_images:
        if set(image['RepoTags']).intersection(dusty_images):
            try:
                client.remove_image(image['Id'])
            except Exception as e:
                logging.info("Couldn't remove image {}".format(image['RepoTags']))
            else:
                log_to_client("Removed Image {}".format(image['RepoTags']))
                removed.append(image)
    return removed
