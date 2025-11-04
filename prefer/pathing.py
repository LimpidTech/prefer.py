from __future__ import annotations

import os
import sys
import typing

DEFAULT_PATH_SUFFIXES = ["etc"]


def get_bin_name() -> str:
    program = os.path.abspath(sys.argv[0])
    bin_name_index = program.rindex(os.sep) + 1
    return program[bin_name_index:]


def get_bin_path() -> str:
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def etc_path(*path: str) -> str:
    return os.path.join(*path, "etc")


def with_bin_path(path: str) -> str:
    return os.path.join(path, get_bin_name())


def get_xdg_config_path() -> typing.Optional[str]:
    xdg_config_path = os.environ.get("XDG_CONFIG_PATH")

    if xdg_config_path:
        return xdg_config_path

    home_dir = os.environ.get("HOME")

    if not home_dir:
        return None

    return os.path.join(home_dir, ".config")


def get_posix_paths() -> list[typing.Optional[str]]:
    xdg_path = get_xdg_config_path()
    home = os.environ.get("HOME")

    paths: list[typing.Optional[str]] = [xdg_path]

    if xdg_path:
        paths.append(os.path.join(xdg_path, get_bin_name()))

    if home:
        paths.extend([etc_path(home), home])

    paths.extend(
        [
            etc_path("/usr/local"),
            etc_path("/usr"),
            etc_path("/"),
        ]
    )

    return paths


def get_windows_paths() -> list[typing.Optional[str]]:
    env_vars = [
        os.environ.get("USERPROFILE"),
        os.environ.get("LOCALPROFILE"),
        os.environ.get("APPDATA"),
        os.environ.get("CommonProgramFiles"),
        os.environ.get("ProgramData"),
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
    ]

    user_paths = [with_bin_path(path) for path in env_vars if path]

    system_root = os.environ.get("SystemRoot")
    system_paths: list[typing.Optional[str]] = []
    if system_root:
        system_paths = [
            os.path.join(system_root, "system"),
            os.path.join(system_root, "system32"),
        ]

    return user_paths + system_paths


SYSTEM_PATH_FACTORIES: dict[
    str, typing.Callable[[], list[typing.Optional[str]]]
] = {
    "posix": get_posix_paths,
    "win32": get_windows_paths,
}


def get_base_paths() -> list[str]:
    return [etc_path(os.getcwd()), os.getcwd()]


def ensure_unique(paths: list[typing.Optional[str]]) -> list[str]:
    results: list[str] = []
    found_paths: set[str] = set()

    for path in paths:
        if not path or path in found_paths:
            continue

        found_paths.add(path)
        results.append(os.path.join(path))

    return results


def get_system_paths(system: str = os.name) -> list[str]:
    paths_list: list[typing.Optional[str]] = list(get_base_paths())
    path_factory = SYSTEM_PATH_FACTORIES.get(system)

    if path_factory is not None:
        paths_list.extend(path_factory())

    paths_list.append(get_bin_path())
    return ensure_unique(paths_list)
