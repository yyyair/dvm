import pathlib

from typer import Typer

from dvm.core.config import Config
from dvm.core.file_tracker import (
    track_new_file,
    set_handler,
    open_tracked_file,
    remove_tracked_file,
    update_all_files, show_file_info,
)
from dvm.core.files import FileType

app = Typer()


@app.command(name="list")
def list_files() -> None:
    config = Config.load_from_disk()
    files = config.tracked_files
    print("\n".join(str(file.original_path) for file in files))


@app.command(name="add")
def add_file(path: pathlib.Path) -> None:
    track_new_file(path)


@app.command(name="remove")
def remove_file(name: str) -> None:
    remove_tracked_file(name)


@app.command(name="update")
def update_cache() -> None:
    update_all_files()


@app.command(name="open")
def open_file(name: str) -> None:
    open_tracked_file(name)


@app.command(name="set-handler")
def add_file_handler(path: pathlib.Path, type: FileType) -> None:
    set_handler(path, type)

@app.command(name='info')
def print_file_info(name: str) -> None:
    show_file_info(name)

def run_app() -> None:
    app()
