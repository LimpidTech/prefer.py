import os
import sys
import unittest

from prefer import pathing

os.environ['XDG_CONFIG_PATH'] = ''


def get_default_config_path():
    return os.path.join(os.environ.get('HOME'), '.config')


def test_get_bin_path_gets_path_to_program_from_argv():
    bin_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    assert pathing.get_bin_path() == bin_path


def test_get_bin_name_gets_name_of_program_from_argv():
    bin_name = sys.argv[0]

    try:
        bin_name = bin_name[sys.argv[0].rindex(os.sep) + 1:]
    except ValueError:
        pass

    assert pathing.get_bin_name() == bin_name


def test_etc_path_appends_etc_to_input():
    assert pathing.etc_path('/usr') == '/usr/etc'


def test_path_generation_for_posix():
    default_config_path = get_default_config_path()

    expectation = [
        pathing.etc_path(os.getcwd()),
        os.getcwd(),
        default_config_path,
        os.path.join(default_config_path, pathing.get_bin_name()),
        pathing.etc_path(os.environ.get('HOME')),
        os.environ.get('HOME'),
        '/usr/local/etc',
        '/usr/etc',
        '/etc',
    ]

    assert pathing.get_system_paths('posix') == expectation


def test_path_generation_uses_xdg_config_path():
    default_config_path = get_default_config_path()
    xdg_config_path = os.path.join(os.getcwd(), '.dotfiles')

    os.environ['XDG_CONFIG_PATH'] = xdg_config_path
    all_paths = pathing.get_system_paths('posix')

    assert xdg_config_path in all_paths
    assert default_config_path not in all_paths
