from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from gimpformats.gimpXcfDocument import GimpDocument

from textdata import get_texts


def create_dataframe(path: Path) -> pd.DataFrame | None:
    texts = get_texts(GimpDocument(str(path)))
    if (l := len(texts)) == 0:
        return None
    return pd.DataFrame({path.stem: texts, f"{path.stem} (번역)": [None] * l})


def create_sheet_from(glob: str) -> pd.DataFrame | None:
    raw = (create_dataframe(path) for path in Path("연재").glob(f"{glob}*.xcf"))
    df = [d for d in raw if d is not None]
    if len(df) == 0:
        return None
    return pd.concat(df, axis="columns").sort_index(axis="columns")


def main() -> None:
    NUM_CORES = 7
    it = (f"{i}화" for i in range(1, 8 + 1))
    with Pool(NUM_CORES) as pool, pd.ExcelWriter("번역.xlsx") as writer:
        results = [pool.apply_async(create_sheet_from, args=(s,)) for s in it]
        output = [r.get() for r in results]
        for i, df in enumerate(output, start=1):
            if df is not None:
                df.to_excel(writer, sheet_name=f"{i:02}화")


if __name__ == "__main__":
    Path("번역").mkdir(exist_ok=True)
    main()
