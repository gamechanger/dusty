from . import constants
from .source import Repo
from .compiler.compose.common import container_code_path
from .systems.docker.common import spec_for_service
from .systems.rsync import sync_local_path_to_vm

def _write_commands_to_file(list_of_commands, file_location):
    with open(file_location, 'w+') as f:
        for command in list_of_commands:
            f.write('{} \n'.format(command))

def _compile_docker_commands(app_name, assembled_specs):
    """ This is used to compile the command that will be run when the docker container starts
    up. This command has to install any libs that the app uses, run the `always` command, and
    run the `once` command if the container is being launched for the first time """
    app_spec = assembled_specs['apps'][app_name]
    first_run_file = constants.FIRST_RUN_FILE_PATH
    commands = _lib_install_commands_for_app(app_name, assembled_specs)
    commands.append("cd {}".format(container_code_path(app_spec)))
    commands.append("export PATH=$PATH:{}".format(container_code_path(app_spec)))
    commands.append("if [ ! -f {} ]".format(first_run_file))
    once_commands = app_spec['commands']["once"]
    commands.append("then mkdir -p {}; touch {}".format(constants.RUN_DIR, first_run_file))
    if once_commands:
        commands += once_commands
    commands.append("fi")
    commands += app_spec['commands']['always']
    return commands

def _get_test_image_setup_commands(app_or_lib_name, expanded_specs, testing_spec):
    commands = lib_install_commands_for_app_or_lib(app_or_lib_name, expanded_specs)
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

def make_up_command_files(assembled_specs):
    for app_name in assembled_specs['apps'].keys():
        spec = assembled_specs['apps'][app_name]
        commands = _compile_docker_commands(app_name, assembled_specs)
        command_file_name = dusty_command_file_name(app_name)
        local_path = '{}/{}/{}'.format(constants.COMMAND_FILES_DIR, app_name, command_file_name)
        _write_commands_to_file(commands, local_path)
        script_specs = spec['scripts']
        for script_spec in script_specs:
            commands = ["cd {}".format(container_code_path(spec))] + script_spec['command']
            commands[-1] = '{} $@'.format(commands[-1])
            command_file_name = dusty_command_file_name(app_name, script_name=script_spec['name'])
            local_path = '{}/{}/{}'.format(constants.COMMAND_FILES_DIR, app_name, command_file_name)
            _write_commands_to_file(commands, local_path)
    sync_local_path_to_vm(constants.COMMAND_FILES_DIR, constants.VM_COMMAND_FILES_DIR)

def make_test_command_files(expanded_specs):
    for app_or_lib_spec in expanded_specs.get_apps_and_libs():
        test_spec = app_or_lib_spec['test']
        if test_spec and test_spec['once']:
            commands = _get_test_image_setup_commands(app_or_lib_spec.name, expanded_specs, test_spec)
            command_file_name = dusty_command_file_name(app_or_lib_spec.name)
            local_path = '{}/{}/test/{}'.format(constants.COMMAND_FILES_DIR, app_or_lib_spec.name, command_file_name)
            _write_commands_to_file(commands, local_path)
            suite_specs = test_spec['suites']
            for suite_spec in suite_specs:
                commands = ["cd {}".format(container_code_path(app_or_lib_spec))] + suite_spec['command']
                commands[-1] = '{} $@'.format(commands[-1])
                command_file_name = dusty_command_file_name(app_or_lib_spec.name, test_name=suite_spec['name'])
                local_path = '{}/{}/test/{}'.format(constants.COMMAND_FILES_DIR, app_or_lib_spec.name, command_file_name)
                _write_commands_to_file(commands, local_path)

    sync_local_path_to_vm(constants.COMMAND_FILES_DIR, constants.VM_COMMAND_FILES_DIR)
