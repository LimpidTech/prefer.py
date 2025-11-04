import os
import sys
from unittest import mock

from prefer import pathing

MOCK_BIN_NAME = "Mock Bin Name"


def unique(subject):
    items = set()
    result = []

    for item in subject:
        if item in items:
            continue

        items.add(item)
        result.append(item)

    return result


def get_default_config_path():
    return os.path.join(os.environ.get("HOME"), ".config")


def test_get_bin_path_gets_path_to_program_from_argv():
    bin_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    assert pathing.get_bin_path() == bin_path


def test_get_bin_name_gets_name_of_program_from_argv():
    bin_name = sys.argv[0]

    try:
        bin_name = bin_name[sys.argv[0].rindex(os.sep) + 1 :]
    except ValueError:
        pass

    assert pathing.get_bin_name() == bin_name


def test_etc_path_appends_etc_to_input():
    assert pathing.etc_path("/usr") == os.path.join("/usr", "etc")


def test_path_generation_for_posix():
    mock_home = "/home/testuser"
    mock_cwd = "/home/testuser/project"
    mock_bin_path = "/usr/bin"
    mock_bin_name = "testapp"

    with mock.patch.dict(
        os.environ, {"HOME": mock_home, "XDG_CONFIG_PATH": ""}
    ):
        with mock.patch("prefer.pathing.os.getcwd", return_value=mock_cwd):
            with mock.patch(
                "prefer.pathing.get_bin_path", return_value=mock_bin_path
            ):
                with mock.patch(
                    "prefer.pathing.get_bin_name", return_value=mock_bin_name
                ):
                    default_config_path = os.path.join(mock_home, ".config")

                    result = pathing.get_system_paths("posix")
                    expected = unique(
                        [
                            pathing.etc_path(mock_cwd),
                            mock_cwd,
                            default_config_path,
                            os.path.join(default_config_path, mock_bin_name),
                            pathing.etc_path(mock_home),
                            mock_home,
                            pathing.etc_path("/usr/local"),
                            pathing.etc_path("/usr"),
                            pathing.etc_path("/"),
                            mock_bin_path,
                        ]
                    )

                    assert result == expected


def test_path_generation_for_win32():
    os.environ.update(
        {
            "USERPROFILE": "USERPROFILE",
            "LOCALPROFILE": "LOCALPROFILE",
            "APPDATA": "APPDATA",
            "CommonProgramFiles": "CommonProgramFiles",
            "ProgramData": "ProgramData",
            "ProgramFiles": "D:\\Program Files",
            "ProgramFiles(x86)": "D:\\Program Files (x86)",
            "SystemRoot": "C:\\Windows",
        }
    )

    assert pathing.get_system_paths(system="win32") == unique(
        [
            pathing.etc_path(os.getcwd()),
            os.path.join(os.getcwd()),
            os.path.join("USERPROFILE", pathing.get_bin_name()),
            os.path.join("LOCALPROFILE", pathing.get_bin_name()),
            os.path.join("APPDATA", pathing.get_bin_name()),
            os.path.join("CommonProgramFiles", pathing.get_bin_name()),
            os.path.join("ProgramData", pathing.get_bin_name()),
            os.path.join("D:\\Program Files", pathing.get_bin_name()),
            os.path.join("D:\\Program Files (x86)", pathing.get_bin_name()),
            os.path.join("C:\\Windows", "system"),
            os.path.join("C:\\Windows", "system32"),
            pathing.get_bin_path(),
        ]
    )


def test_path_generation_uses_xdg_config_path():
    mock_home = "/home/testuser"
    mock_cwd = "/home/testuser/project"
    xdg_config_path = "/home/testuser/.dotfiles"
    default_config_path = os.path.join(mock_home, ".config")

    with mock.patch.dict(
        os.environ, {"HOME": mock_home, "XDG_CONFIG_PATH": xdg_config_path}
    ):
        with mock.patch("prefer.pathing.os.getcwd", return_value=mock_cwd):
            all_paths = pathing.get_system_paths("posix")

            assert xdg_config_path in all_paths
            assert default_config_path not in all_paths


def test_get_xdg_config_path_returns_none_when_no_home():
    with mock.patch.dict(
        os.environ, {"HOME": "", "XDG_CONFIG_PATH": ""}, clear=True
    ):
        result = pathing.get_xdg_config_path()
        assert result is None


def test_get_xdg_config_path_returns_xdg_when_set():
    xdg_path = "/custom/config"
    with mock.patch.dict(os.environ, {"XDG_CONFIG_PATH": xdg_path}):
        result = pathing.get_xdg_config_path()
        assert result == xdg_path


def test_get_xdg_config_path_returns_default_when_home_set():
    home_path = "/home/user"
    with mock.patch.dict(
        os.environ, {"HOME": home_path, "XDG_CONFIG_PATH": ""}
    ):
        result = pathing.get_xdg_config_path()
        assert result == os.path.join(home_path, ".config")


def test_get_system_paths_handles_unknown_system():
    mock_cwd = "/test/path"
    mock_bin_path = "/usr/bin"

    with mock.patch("prefer.pathing.os.getcwd", return_value=mock_cwd):
        with mock.patch(
            "prefer.pathing.get_bin_path", return_value=mock_bin_path
        ):
            result = pathing.get_system_paths("unknown_system")

            assert pathing.etc_path(mock_cwd) in result
            assert mock_cwd in result
            assert mock_bin_path in result


def test_ensure_unique_filters_none_values():
    paths = ["/path1", None, "/path2", "", "/path1", "/path3"]
    result = pathing.ensure_unique(paths)

    assert None not in result
    assert "" not in result
    assert len([p for p in result if p == "/path1"]) == 1
