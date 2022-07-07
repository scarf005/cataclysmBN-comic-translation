import re
from html.parser import HTMLParser
from typing import Pattern

from gimpformats.gimpXcfDocument import GimpDocument, GimpLayer

STRIP_PARENS = re.compile(r"(?<=\().*(?=\))")
STRIP_QUOTES = re.compile(r"(?<=\").*(?=\")")


def strip_re(text: str, pattern: Pattern = STRIP_PARENS) -> str:
    if (res := pattern.search(text)) is not None:
        return res.group()
    else:
        return text


class MarkUpParser(HTMLParser):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.text: str = ""

    def handle_data(self, data: str) -> None:
        self.text += data


def parse_text_markup(v: str) -> str:
    "assumes markup data is always valid"
    parser = MarkUpParser()
    parser.feed(v)
    return parser.text


def parse_text(data: str) -> str:
    for t in data.rstrip("\x00").splitlines():
        k, raw_v = strip_re(t).split(" ", 1)
        v = strip_re(raw_v, STRIP_QUOTES)
        match k:
            case "text":
                return v
            case "markup":
                return parse_text_markup(v)

    raise ValueError(f"No text found in {data}")


def get_text(textlayer: GimpLayer) -> str:
    "assumes textlayer always contains text as its first parasite"
    return parse_text(textlayer.parasites[0].data.decode())  # type:ignore


def get_texts(project: GimpDocument) -> list[str]:
    return [get_text(layer) for layer in project.layers if is_text(layer)]


def is_text(layer: GimpLayer) -> bool:
    return "gimp-text-layer" in {p.name for p in layer.parasites}


if __name__ == "__main__":
    from pprint import pprint

    project = GimpDocument("연재/1화-01.xcf")
    pprint(get_texts(project))
