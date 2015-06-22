def spec_for_service(app_or_lib_name, expanded_specs):
    if app_or_lib_name in expanded_specs['apps']:
        return expanded_specs['apps'][app_or_lib_name]
    return expanded_specs['libs'][app_or_lib_name]
