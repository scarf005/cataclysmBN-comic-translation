import re
from html.parser import HTMLParser
from textwrap import dedent

from flupy import flu
from numpy import byte
from typing_extensions import Self

STRIP_PARENS = re.compile(r"(?<=\().*(?=\))")


def strip_parens(text: str) -> str:
    if (res := STRIP_PARENS.search(text)) is not None:
        return res.group()
    return text


class MarkUpParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text: str = ""

    def handle_data(self, data: str):
        self.text += data


def get_text(data: str) -> str:
    raw = data.rstrip("\x00").splitlines()
    for t in raw:
        k, v = strip_parens(t).split(" ", 1)
        match k:
            case "text":
                return v
            case "markup":
                v = v.replace("\\", "").replace('"', "")
                parser = MarkUpParser()
                parser.feed(v)
                if len(parser.text) == 0:
                    raise ValueError(f"{v} is not a valid markup")
                return parser.text

    raise ValueError(f"No text found in {data}")


if __name__ == "__main__":
    from gimpformats.gimpXcfDocument import GimpDocument

    project = GimpDocument("연재/1화-01.xcf")
    for layer in project.layers:
        data: bytearray = layer.parasites[0].data  # type: ignore
        print(get_text(data.decode()))

