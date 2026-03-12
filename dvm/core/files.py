import enum
import pathlib

from pydantic import BaseModel

from dvm.core.utils import calculate_file_hash


class FileType(str, enum.Enum):
    CUSTOM = "custom"
    PE = "pe"
    ELF = "elf"
    MACHO = "macho"
    JAR = "jar"
    APK = "apk"


FILE_EXTENSIONS: dict[str, FileType] = {
    "exe": FileType.PE,
    "dll": FileType.PE,
    "so": FileType.ELF,
    "dylib": FileType.MACHO,
    "apk": FileType.APK,
    "jar": FileType.JAR,
}


class File(BaseModel):
    original_path: pathlib.Path
    cached_path: pathlib.Path
    type: FileType

    @property
    def name(self) -> str:
        return self.original_path.stem

    @property
    def is_stale(self) -> bool:
        return calculate_file_hash(self.original_path) != calculate_file_hash(
            self.cached_path
        )

    @property
    def cached_hash(self) -> str:
        return calculate_file_hash(self.cached_path)


class FileHandler(BaseModel):
    supported_types: list[FileType]
    executable_path: pathlib.Path
