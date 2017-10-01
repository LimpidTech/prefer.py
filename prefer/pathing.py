import functools
import os
import typing
import sys

DEFAULT_PATH_SUFFIXES = ['etc']


def get_bin_name():
    program = os.path.abspath(sys.argv[0])
    bin_name_index = program.rindex(os.sep) + 1
    return program[bin_name_index:]


def get_bin_path():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def etc_path(*path):
    return os.path.join(*path, 'etc')


def with_bin_path(path: str):
    return os.path.join(path, get_bin_name())


def get_xdg_config_path():
    xdg_config_path = os.environ.get('XDG_CONFIG_PATH')

    if xdg_config_path:
        return xdg_config_path

    home_dir = os.environ.get('HOME')

    if not home_dir:
        return None

    return os.path.join(home_dir, '.config')


def get_posix_paths():
    return [
        get_xdg_config_path(),
        os.path.join(get_xdg_config_path(), get_bin_name()),
        etc_path(os.environ.get('HOME')),
        os.environ.get('HOME'),
        etc_path('/usr/local'),
        etc_path('/usr'),
        etc_path('/'),
    ]


def get_windows_paths():
    user_paths = [
        path
        for path in map(
            with_bin_path, (
                os.environ.get('USERPROFILE'),
                os.environ.get('LOCALPROFILE'),
                os.environ.get('APPDATA'),
                os.environ.get('CommonProgramFiles'),
                os.environ.get('ProgramData'),
                os.environ.get('ProgramFiles'),
                os.environ.get('ProgramFiles(x86)'),
            )
        )
    ]

    return user_paths + [
        os.path.join(os.environ.get('SystemRoot'), 'system'),
        os.path.join(os.environ.get('SystemRoot'), 'system32'),
    ]


SYSTEM_PATH_FACTORIES = {
    'posix': get_posix_paths,
    'win32': get_windows_paths,
}


def get_base_paths():
    return [etc_path(os.getcwd()), os.getcwd()]


def ensure_unique(paths: typing.List[str]):
    results = []

    found_paths: typing.Set[str] = set()

    for path in paths:
        if not path or path in found_paths:
            continue

        found_paths.add(path)
        results.append(os.path.join(path))

    return results


def get_system_paths(system: str=os.name):
    paths = get_base_paths()
    path_factory = SYSTEM_PATH_FACTORIES.get(system)

    if path_factory is not None:
        paths += path_factory()

    paths.append(get_bin_path())
    return ensure_unique(paths + path_factory())
