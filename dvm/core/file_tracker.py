import glob
import pathlib
import re
import shutil
import subprocess
from structlog import get_logger
import xdg_base_dirs

from dvm.core.config import Config
from dvm.core.files import File, FileType, FILE_EXTENSIONS, FileHandler
import os


class FileAlreadyTracked(Exception):
    pass


class UnknownFileType(Exception):
    pass


class FileNotFound(Exception):
    pass


class NoFileHandler(Exception):
    pass


class MultipleFileError(Exception):
    pass

logger = get_logger("file-tracker")

def get_cache_base() -> pathlib.Path:
    return xdg_base_dirs.xdg_data_home() / "dvm"


def find_file_by_regex(name_regex: str, files: list[File]) -> File:
    matches = [file for file in files if len(re.findall(name_regex, file.name)) > 0]
    if len(matches) == 0:
        raise FileNotFound(f"File {name_regex} not found")
    elif len(matches) > 1:
        raise MultipleFileError()
    else:
        return matches[0]


def find_file_type_handler(
    file_type: FileType, handlers: list[FileHandler]
) -> FileHandler:
    for handler in handlers:
        if file_type in handler.supported_types:
            return handler
    raise NoFileHandler(f"No file handler for {file_type.name}")


def track_new_file(
    path: pathlib.Path,
    type_override: FileType | None = None,
    name_override: str | None = None,
) -> None:
    config = Config.load_from_disk()
    # Check if already tracked
    for tracked_file in config.tracked_files:
        if tracked_file.original_path == path:
            raise FileAlreadyTracked()

    # Determine file type
    file_extension = pathlib.Path(path).suffix[1:]
    file_type = FILE_EXTENSIONS.get(file_extension, None)
    if type_override is not None:
        file_type = type_override
    if file_type is None:
        raise UnknownFileType()

    # Copy to cache
    cache_name = path.name
    if name_override is not None:
        cache_name = name_override
    cache_path = get_cache_base() / cache_name
    os.makedirs(get_cache_base(), exist_ok=True)
    shutil.copy(path, cache_path)

    # Add to config
    file = File(original_path=path, cached_path=cache_path, type=file_type)
    config.tracked_files.append(file)
    config.save_to_disk()

def delete_file_cache(file: File) -> None:
    for metadata_file in glob.glob(f"{file.cached_path}*"):
        os.remove(metadata_file)


def remove_tracked_file(name: str) -> None:
    config = Config.load_from_disk()
    file = find_file_by_regex(name, config.tracked_files)
    delete_file_cache(file)
    config.tracked_files.remove(file)
    config.save_to_disk()

def update_tracked_file(name: str) -> None:
    config = Config.load_from_disk()
    file = find_file_by_regex(name, config.tracked_files)
    if not file.is_stale:
        return
    delete_file_cache(file)
    shutil.copy(file.original_path, file.cached_path)

def update_all_files() -> None:
    config = Config.load_from_disk()
    for file in config.tracked_files:
        update_tracked_file(file.name)

def open_tracked_file(name: str) -> None:
    config = Config.load_from_disk()
    file = find_file_by_regex(name_regex=name, files=config.tracked_files)
    if file.is_stale:
        logger.warning(f"Opening stale file: {file.original_path}")
    handler = find_file_type_handler(file.type, config.file_handlers)
    subprocess.Popen(
        [str(handler.executable_path), str(file.cached_path)], start_new_session=True
    )


def set_handler(executable_path: pathlib.Path, for_type: FileType) -> None:
    config = Config.load_from_disk()
    try:
        handler = find_file_type_handler(for_type, config.file_handlers)
    except NoFileHandler:
        handler = FileHandler(executable_path=executable_path, supported_types=[])
        config.file_handlers.append(handler)
    if for_type not in handler.supported_types:
        handler.supported_types.append(for_type)
    if executable_path != handler.executable_path:
        handler.executable_path = executable_path
    config.save_to_disk()
