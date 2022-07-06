#!/usr/bin/env python3
import textwrap
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from gimpformats.gimpXcfDocument import GimpDocument, GimpLayer

from textdata import get_text


def is_text(layer: GimpLayer) -> bool:
    return any(p.name.startswith("gimp-text-layer") for p in layer.parasites)


@dataclass
class TextLayer:
    _layer: GimpLayer
    name: str = field(init=False)
    data: TextData = field(init=False)

    def __post_init__(self):
        self.name = str(self._layer.name)
        if (data := self._layer.parasites[0].data) is not None:
            self.data = TextData.decode(data)

    @property
    def text(self) -> str:
        return self.data.text

    @text.setter
    def text(self, text: str) -> None:
        self.data.text = text

    def __repr__(self):
        return (
            f"layer: {self.name}"
            + "\ntextdata:\n"
            + textwrap.indent(repr(self.data), " ")
        )


class Project:
    def __init__(self, path: Path | str) -> None:
        self._project = GimpDocument(str(path))
        self._layers = [l for l in enumerate(self._project.layers)]
        self.textlayers = [TextLayer(l) for _, l in self._layers if is_text(l)]

    def __iter__(self):
        return iter(self.textlayers)

    def __len__(self):
        return len(self.textlayers)


from pathlib import Path

for layer in Project("연재/1화-01.xcf"):
    print(get_text(data.decode()))
