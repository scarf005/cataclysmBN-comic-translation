import re
from textwrap import dedent

from typing_extensions import Self

STRIP_PARENS = re.compile(r"(?<=\().*(?=\))")


def strip_parens(text: str) -> str:
    if (res := STRIP_PARENS.search(text)) is not None:
        return res.group()
    return text


from pprint import pformat


class TextData:
    def __init__(self, text: str) -> None:
        self.data: dict[str, str] = {}
        for t in text.rstrip("\x00").splitlines():
            k, v = strip_parens(t).split(" ", 1)
            self.data[k] = v
        if self.data is None:
            raise ValueError("Could not parse text data")

    def __repr__(self) -> str:
        return pformat(self.data)

    def __getattr__(self, name: str) -> str:
        if name in self.data:
            return self.data[name]
        raise AttributeError(f"{name} not found")

    def __len__(self) -> int:
        return len(self.raw_with_null)

    @property
    def text(self) -> str:
        if text := self.data.get("text"):
            return text
        elif text := self.data.get("markup"):
            return text
        raise ValueError("No text found")

    @property
    def raw(self) -> str:
        """recreates input text"""
        return "\n".join(f"({k} {v})" for k, v in self.data.items()) + "\n"

    @property
    def raw_with_null(self) -> str:
        """recreates decode()"""
        return self.raw + "\x00"

    def encode(self) -> bytearray:
        b = bytearray()
        b.extend(self.raw_with_null.encode())
        return b

    @classmethod
    def decode(cls, b: bytearray) -> Self:
        return cls(b.decode())


if __name__ == "__main__":
    from gimpformats.gimpXcfDocument import GimpDocument

    project = GimpDocument("연재/1화-01.xcf")
    data: bytearray = project.layers[0].parasites[0].data  # type: ignore
    decoded = data.decode()
    text = decoded.rstrip("\x00")
    print(TextData(text))
    print(TextData(text).text)
    for td in (TextData(text), TextData.decode(data)):
        assert text == td.raw
        assert decoded == td.raw_with_null
        assert data == td.encode()
