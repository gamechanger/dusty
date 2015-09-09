import os

from . import constants
from .source import Repo
from .compiler.compose.common import container_code_path
from .systems.docker.common import spec_for_service
from .systems.rsync import sync_local_path_to_vm
from .path import case_insensitive_rename, parent_dir

def _write_commands_to_file(list_of_commands, app_name, file_location):
    file_location_parent = '{}/{}'.format(constants.COMMAND_FILES_DIR, app_name)
    if os.path.exists(file_location_parent):
        # This looks insane but it's necessary to handle case-insensitive host filesystems
        # like HFS on Mac. The filesystems in our VM are case-sensitive, so we need to make
        # sure the case-sensitive representation is consistent.
        case_insensitive_rename(file_location_parent, file_location_parent)
    else:
        os.makedirs(file_location_parent)
    if not os.path.exists(parent_dir(file_location)):
        os.makedirs(parent_dir(file_location))
    # We need to do this for similar reasons of case-insensitivity
    if os.path.exists(file_location):
        os.remove(file_location)
    with open(file_location, 'w+') as f:
        for command in list_of_commands:
            f.write('{} \n'.format(command))

def _tee_output_commands(command_to_tee):
    tee_function_name = 'tee_{}'.format(command_to_tee)
    commands = [
        '{} () {{'.format(tee_function_name),
        'PIPEFILE={}_pipe_file'.format(tee_function_name),
        'rm -f $PIPEFILE',
        'mkfifo $PIPEFILE',
        '(tee {}.log < $PIPEFILE || true; rm -f $PIPEFILE) &'.format(os.path.join(constants.CONTAINER_LOG_PATH, command_to_tee)),
        '{} 2>&1 > $PIPEFILE'.format(command_to_tee),
        '}',
        tee_function_name
    ]
    return commands

def _hosts_export_commands(port_spec):
    if not port_spec['hosts_file']:
        return []
    commands = ['DOCKERHOST=`/sbin/ip route|awk \'/default/ { print $3 }\'`']
    commands.extend(['echo "$DOCKERHOST    {}" >> /etc/hosts'.format(host['host_address'])
        for host in port_spec['hosts_file']])
    return commands

def _get_once_commands(app_spec, port_spec):
    once_commands = _hosts_export_commands(port_spec)
    once_commands += app_spec['commands']['once']
    commands_with_function = []
    if once_commands:
        commands_with_function.append('dusty_once_fn () {')
        commands_with_function += once_commands
        commands_with_function.append('}')
    commands_with_function.append("if [ ! -f {} ]; then".format(constants.FIRST_RUN_FILE_PATH))
    commands_with_function.append("touch {}".format(constants.FIRST_RUN_FILE_PATH))
    if once_commands:
        commands_with_function += _tee_output_commands('dusty_once_fn')

    commands_with_function.append("fi")
    return commands_with_function

def _get_always_commands(app_spec):
    commands_with_function = []
    always_commands = app_spec['commands']['always']
    if always_commands:
        commands_with_function.append('dusty_always_fn () {')
        commands_with_function += always_commands
        commands_with_function.append('}')
        commands_with_function.append('dusty_always_fn')
    return commands_with_function

def _copy_asset_command(asset):
    return 'if [ -f {0} ]; then cp {0} {1}; fi'.format(
        os.path.join(constants.IN_CONTAINER_ASSETS_DIR, asset['name']), asset['path'])

def _copy_assets_commands_for_lib(lib_spec):
    return [_copy_asset_command(asset) for asset in lib_spec['assets']]

def _copy_assets_commands_for_app(app_spec, assembled_specs):
    commands = []
    for asset in app_spec['assets']:
        commands.append(_copy_asset_command(asset))
    for lib in app_spec['depends']['libs']:
        commands.extend(_copy_assets_commands_for_lib(assembled_specs['libs'][lib]))
    return commands

def _compile_docker_commands(app_name, assembled_specs, port_spec):
    """ This is used to compile the command that will be run when the docker container starts
    up. This command has to install any libs that the app uses, run the `always` command, and
    run the `once` command if the container is being launched for the first time """
    app_spec = assembled_specs['apps'][app_name]
    commands = ['set -e']
    commands += _lib_install_commands_for_app(app_name, assembled_specs)
    if app_spec['mount']:
        commands.append("cd {}".format(container_code_path(app_spec)))
        commands.append("export PATH=$PATH:{}".format(container_code_path(app_spec)))
    commands += _copy_assets_commands_for_app(app_spec, assembled_specs)
    commands += _get_once_commands(app_spec, port_spec)
    commands += _get_always_commands(app_spec)
    return commands

def _get_test_image_setup_commands(app_or_lib_name, expanded_specs, testing_spec):
    commands = ['set -e']
    commands += lib_install_commands_for_app_or_lib(app_or_lib_name, expanded_specs)
    commands += ['cd {}'.format(container_code_path(spec_for_service(app_or_lib_name, expanded_specs)))]
    commands += testing_spec['once']
    return commands

def _lib_install_commands_for_libs(assembled_specs, libs):
    commands = []
    for lib in libs:
        lib_spec = assembled_specs['libs'][lib]
        install_commands = _lib_install_commands(lib_spec)
        if install_commands:
            commands += install_commands
    return commands

def _lib_install_commands_for_app(app_name, assembled_specs):
    """ This returns a list of all the commands that will install libraries for a
    given app """
    libs = assembled_specs['apps'][app_name]['depends']['libs']
    return _lib_install_commands_for_libs(assembled_specs, libs)

def _lib_install_commands_for_lib(app_name, assembled_specs):
    """ This returns a list of all the commands that will install libraries for a
    given lib """
    libs = assembled_specs['libs'][app_name]['depends']['libs']
    return _lib_install_commands_for_libs(assembled_specs, libs)

def lib_install_commands_for_app_or_lib(app_or_lib_name, assembled_specs):
    if app_or_lib_name in assembled_specs['apps']:
        return _lib_install_commands_for_app(app_or_lib_name, assembled_specs)
    return _lib_install_commands_for_lib(app_or_lib_name, assembled_specs)

def _lib_install_commands(lib_spec):
    """ This returns a single commmand that will install a library in a docker container """
    if not lib_spec['install']:
        return []
    return ["cd {}".format(lib_spec['mount'])] + lib_spec['install']

def dusty_command_file_name(app_or_lib_name, script_name=None, test_name=None):
    command_file_name = 'dusty_command_file_{}'.format(app_or_lib_name)
    if script_name:
        command_file_name = '{}_script_{}'.format(command_file_name, script_name)
    elif test_name:
        command_file_name = '{}_test_{}'.format(command_file_name, test_name)
    return "{}.sh".format(command_file_name)

def _write_up_command(app_name, assembled_specs, port_spec):
    commands = _compile_docker_commands(app_name, assembled_specs, port_spec)
    command_file_name = dusty_command_file_name(app_name)
    local_path = '{}/{}/{}'.format(constants.COMMAND_FILES_DIR, app_name, command_file_name)
    _write_commands_to_file(commands, app_name, local_path)

def _write_up_script_command(app_name, app_spec, script_spec):
    commands = ["cd {}".format(container_code_path(app_spec))] + script_spec['command']
    commands[-1] = '{} $@'.format(commands[-1])
    command_file_name = dusty_command_file_name(app_name, script_name=script_spec['name'])
    local_path = '{}/{}/{}'.format(constants.COMMAND_FILES_DIR, app_name, command_file_name)
    _write_commands_to_file(commands, app_name, local_path)

def _write_test_command(app_or_lib_spec, expanded_specs):
    commands = _get_test_image_setup_commands(app_or_lib_spec.name, expanded_specs, app_or_lib_spec['test'])
    command_file_name = dusty_command_file_name(app_or_lib_spec.name)
    local_path = '{}/{}/test/{}'.format(constants.COMMAND_FILES_DIR, app_or_lib_spec.name, command_file_name)
    _write_commands_to_file(commands, app_or_lib_spec.name, local_path)

def _write_test_suite_command(app_or_lib_spec, suite_spec):
    commands = ["cd {}".format(container_code_path(app_or_lib_spec))] + suite_spec['command']
    commands[-1] = '{} $@'.format(commands[-1])
    command_file_name = dusty_command_file_name(app_or_lib_spec.name, test_name=suite_spec['name'])
    local_path = '{}/{}/test/{}'.format(constants.COMMAND_FILES_DIR, app_or_lib_spec.name, command_file_name)
    _write_commands_to_file(commands, app_or_lib_spec.name, local_path)

def make_up_command_files(assembled_specs, port_spec):
    for app_name in assembled_specs['apps'].keys():
        spec = assembled_specs['apps'][app_name]
        _write_up_command(app_name, assembled_specs, port_spec)
        script_specs = spec['scripts']
        for script_spec in script_specs:
            _write_up_script_command(app_name, spec, script_spec)
    sync_local_path_to_vm(constants.COMMAND_FILES_DIR, constants.VM_COMMAND_FILES_DIR)

def make_test_command_files(app_or_lib_name, expanded_specs):
    app_or_lib_spec = expanded_specs.get_app_or_lib(app_or_lib_name)
    test_spec = app_or_lib_spec['test']
    if test_spec and test_spec['once']:
        suite_specs = test_spec['suites']
        _write_test_command(app_or_lib_spec, expanded_specs)
        for suite_spec in suite_specs:
            _write_test_suite_command(app_or_lib_spec, suite_spec)
    sync_local_path_to_vm(constants.COMMAND_FILES_DIR, constants.VM_COMMAND_FILES_DIR)
