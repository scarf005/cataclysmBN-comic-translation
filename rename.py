#!/usr/bin/env python3

from pathlib import Path
from pprint import pprint

from flupy import flu

res = (
    flu(Path("연재").glob("*-*.xcf"))
    .map(lambda e: (e, e.stem.split("-")))
    .filter(lambda t: len(t[1]) == 2)
    .filter(lambda t: t[1][1].isdigit())
    .map(lambda t: (t[0], t[1][0], f"{t[1][1]:>02}"))
    .sort(lambda t: (t[1], t[2]))
    .map(lambda t: (t[0], f"연재/{t[1]}-{t[2]}.xcf"))
    .filter(lambda t: str(t[0]) != t[1])
    .collect()
)

pprint(res)
