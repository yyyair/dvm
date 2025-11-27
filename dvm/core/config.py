import json
import os

import xdg_base_dirs
from pydantic import BaseModel
import enum
import pathlib

from dvm.core.files import FileHandler, File


class Config(BaseModel):
    file_handlers: list[FileHandler]
    tracked_files: list[File]

    @staticmethod
    def storage_path() -> pathlib.Path:
        return xdg_base_dirs.xdg_config_home() / "dvm.cfg"

    @classmethod
    def load_from_disk(cls) -> "Config":
        stored_config = cls.storage_path()
        if stored_config.exists():
            return cls.model_validate(json.loads(stored_config.read_text()))
        else:
            empty_config = Config(file_handlers=[], tracked_files=[])
            return empty_config

    def save_to_disk(self) -> None:
        path = self.storage_path()
        os.makedirs(path.parent, exist_ok=True)
        path.write_text(self.model_dump_json())
