import enum
import shutil
from collections import defaultdict
from collections.abc import Callable, Iterator
from pathlib import Path

from .trie import Trie

type CleanerFunc = Callable[[Path], bool]
type Cleaner = tuple[Clean, CleanerFunc]
_cleaners: dict[enum.Flag, list[Cleaner]] = defaultdict(list)


class Clean(enum.Flag):
    NONE = 0
    PYTHON = enum.auto()
    CARGO = enum.auto()
    NODE = enum.auto()

    ALL = PYTHON | CARGO | NODE

    def register(self, func: CleanerFunc) -> CleanerFunc:
        for flag in self:
            _cleaners[flag].append((self, func))
        return func

    def cleaners(self) -> list[Cleaner]:
        return [func for flag in self for func in _cleaners[flag]]


def clean(folders: list[Path], types: Clean) -> Iterator[tuple[Clean, Path]]:
    for parts in Trie(None, *(folder.parts for folder in folders)):
        folder = Path(*parts)
        if folder.exists():
            yield from clean_folder(folder, types.cleaners())


def remove(path: Path):
    shutil.rmtree(path, ignore_errors=True)


def clean_folder(folder: Path, cleaners: list[Cleaner]) -> Iterator[tuple[Clean, Path]]:
    for path in folder.iterdir():
        if path.name.startswith("."):
            continue
        if (flags := clean_path(path, cleaners)) is not None:
            yield flags, path
            continue

        if path.is_dir():
            yield from clean_folder(path, cleaners)


def clean_path(path: Path, cleaners: list[Cleaner]) -> Clean | None:
    for flag, cleaner in cleaners:
        if cleaner(path):
            return flag
    return None


@Clean.NODE.register
def clean_node_modules(path: Path) -> bool:
    return path.name == "node_modules"


@Clean.CARGO.register
def clean_cargo_target(path: Path) -> bool:
    return path.name == "target" and (path.parent / "Cargo.toml").exists()


@Clean.PYTHON.register
def clean_pycache_folder(path: Path) -> bool:
    return path.name == "__pycache__"


@Clean.PYTHON.register
def clean_pycache_files(path: Path) -> bool:
    return path.suffix == ".pyc"
