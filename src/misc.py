# Python 3.8+ Built-in packages
import os
import re
import time
import platform
from pathlib import Path
from shutil import rmtree
from typing import Tuple, List

# Local packages
from . import config
from . import texts


MAYA_PATH: Path = Path()


def get_bundled_maya_path() -> Path:
    """Get the path to the bundled mayachemtools directory."""
    # Get the directory where this script is located
    current_dir = Path(__file__).resolve().parent.parent
    maya_path = current_dir / "mayachemtools" / "bin"
    return maya_path


# Get path variable. Meant to be cross-platform
def _get_path_env_var() -> str:
    return os.getenv("PATH", None) or os.getenv("Path", None) or os.getenv("path", "")


def system_verification() -> Tuple[bool, List[str]]:
    messages = []
    system_ok = True

    path_env_var = _get_path_env_var()

    if len(path_env_var) == 0:
        system_ok = False
        messages.append("Path environment variable not found on your operating system.")
    else:
        if not re.search("perl", path_env_var, flags=re.IGNORECASE):
            if is_windows():
                system_ok = False
                messages.append(
                    "Perl not found in your path variable. It may mean you didn't installed perl or you haven't added it yet."
                )
            elif not Path("/usr/bin/perl").exists():
                system_ok = False
                messages.append(
                    "Perl not found in /usr/bin. It may mean you didn't installed perl or you haven't added it yet."
                )

        # Use bundled mayachemtools instead of requiring it in PATH
        look_for_maya(path_env_var)

    # check if all FP related dictionary contain the same FP name as keys
    if False in [a in config.FP_AVAILABLE for a in config.FINGERPRINT_CMD]:
        system_ok = False
        messages.append(
            "Configuration problem in the fingerprint setting. Did you add some fingerprints recently ?"
        )

    temp_dir = Path(config.BASE_TEMP_DIR)
    if not temp_dir.is_dir():
        temp_dir.mkdir()
    bin_temp_dir = Path(config.DEFAULT_BINARY_FINGERPRINT_FOLDER)
    if not bin_temp_dir.is_dir():
        bin_temp_dir.mkdir()

    return system_ok, messages


# Perform check for Maya path and set the variable for later use
def look_for_maya(path_env_var: str) -> None:
    global MAYA_PATH

    # First try to use bundled mayachemtools
    bundled_maya = get_bundled_maya_path()
    if _is_maya_path_fine(bundled_maya):
        MAYA_PATH = bundled_maya
        return

    # If bundled version doesn't exist, check PATH
    if re.search("MayaChemTools", path_env_var, flags=re.IGNORECASE):
        MAYA_PATH = Path(_get_path("MayaChemTools"))
    else:
        maya_file_path = Path(config.SAVED_MAYA_PATH_FILE)
        if maya_file_path.is_file():
            MAYA_PATH = Path(maya_file_path.read_text(encoding=config.ENCODING))
            if not _is_maya_path_fine(MAYA_PATH):
                MAYA_PATH = get_file_from_user()
        else:
            MAYA_PATH = get_file_from_user()


def _is_maya_path_fine(maya_path: Path) -> bool:
    return maya_path.is_dir() and maya_path.name == "bin"


# Ask user for maya path file and return it
def get_file_from_user() -> Path:
    file_path_not_ok = True
    print(texts.input_maya_path_help, end="")
    user_provided_path = Path()  # Initialize with empty path
    while file_path_not_ok:
        user_provided_path = Path(input()).resolve()
        if _is_maya_path_fine(user_provided_path):
            file_path_not_ok = False
        else:
            print(texts.input_maya_incorrect, end="")

    Path(config.SAVED_MAYA_PATH_FILE).write_text(
        str(user_provided_path), encoding=config.ENCODING
    )
    return user_provided_path


def get_maya_path() -> Path:
    global MAYA_PATH
    return MAYA_PATH


def get_perl_path() -> Path:
    if is_windows():
        return Path(_get_path("perl(\\\\|/)bin"))
    else:
        return _get_bin_path("perl")


def _path_exists(path: str) -> bool:
    return Path(path).exists()


def is_windows():
    return platform.system() == "Windows"


def is_linux():
    return platform.system() == "Linux"


def is_mac():
    return platform.system() == "Darwin"


# look into the path variable and return the path to the
def _get_path(dirname: str) -> str:
    path_env_var = _get_path_env_var()
    output_path = ""

    # Elucidate environment
    if is_windows():
        path_delimiter = ";"
    else:
        path_delimiter = ":"

    paths = path_env_var.split(path_delimiter)

    for path in paths:
        if re.search(dirname, path, flags=re.IGNORECASE):
            if _path_exists(path):
                output_path = path

    return output_path


def _get_bin_path(bin_name) -> Path:
    bin_path = Path("/usr/bin")
    if bin_path.is_dir():
        p = Path(bin_path, bin_name)
        if p.exists():
            return p
    return Path(bin_name)


def clean_up():
    rmtree(config.BASE_TEMP_DIR)


def chrono(funct):
    def wrapper(*args, **kwargs):
        chrono = time.time()
        r = funct(*args, **kwargs)
        print(
            "\tElapsed time for function {} : {}s\n".format(
                funct.__name__, time.time() - chrono
            ),
            end="",
        )
        return r

    return wrapper
