from . import get_docker_client


def ensure_testing_spec_base_image(testing_spec):
    if 'image' in testing_spec and 'build' in testing_spec:
        raise RuntimeError('Only 1 of `image` and `build` keys are allowed in testing spec')
    elif 'image' in testing_spec:
        return testing_spec['image']
    elif 'build' in testing_spec:
        docker_client = get_docker_client()
        image_tag = 'dusty_testing/image'
        new_image = docker_client.build(path=testing_spec['build'], tag=image_tag)
        return image_tagfrom io import BytesIO
    else:
        raise RuntimeError('One of `image` or `build` is required in testing spec')

def make_installed_requirements_image(base_image_tag, command, image_name):
    docker_client = get_docker_client()
    container = docker_client.create_container(image=base_image_tag, command=command)
    docker_client.start(container=container['Id'])
    #this tagging is not working as of yet
    new_image = docker_client.commit(container=container['Id'], tag=image_name)
    return new_image['Id']

def make_installed_testing_image(testing_spec, new_image_name):
    base_image_tag = ensure_testing_spec_base_image(testing_spec)
    make_installed_requirements_image(base_image_tag, testing_spec['command'], new_image_name)
    return new_image_id
