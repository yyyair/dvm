import hashlib
import pathlib


class NotAFileError(Exception):
    pass


def calculate_file_hash(path: pathlib.Path) -> str:
    if not path.is_file():
        raise NotAFileError(f"{path} is not a file")
    file_hash = hashlib.sha256()
    file_hash.update(path.read_bytes())
    return file_hash.hexdigest()
