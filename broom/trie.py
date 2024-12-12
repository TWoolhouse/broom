from collections.abc import Iterable, Iterator
from typing import Self


class Trie[T, E]:
    type Tree = dict[T | E, Tree]

    def __init__(self, end: E, *words: Iterable[T]) -> None:
        self.end = end
        self._root: Trie.Tree = {}

        self.extend(*words)

    @classmethod
    def from_tree(cls, tree: Tree, end: E) -> Self:
        self = cls(end)
        self._root = tree
        return self

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}<{self.end}>{self._root}"

    def insert(self, word: Iterable[T]) -> Self:
        d = self._root
        for char in word:
            if char not in d:
                d[char] = {}
            d = d[char]
        d[self.end] = {}

        return self

    def extend(self, *words: Iterable[T]) -> Self:
        for word in words:
            self.insert(word)
        return self

    def __bool__(self) -> bool:
        return bool(self._root)

    def __contains__(self, word: Iterable[T]) -> bool:
        d = self._root
        return all((d := d.get(char, None)) is not None for char in word)

    def __getitem__(self, word: Iterable[T]) -> Self:
        d = self._root
        for char in word:
            d = d[char]
        return self.from_tree(d, self.end)

    def __iter__(self) -> Iterator[list[T]]:
        return self._iter(self._root)

    def _iter(self, level: Tree) -> Iterator[list[T]]:
        for key, value in level.items():
            if key == self.end:
                yield []
            else:
                for v in self._iter(value):
                    v.insert(0, key)
                    yield v
