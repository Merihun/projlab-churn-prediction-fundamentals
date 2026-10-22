"""python -m fernhill_box    write data/raw/ (again) in this folder: Fernhill Box's export up to 30 September 2026"""

import sys
from pathlib import Path

from . import data


def main(argv: list[str]) -> int:
    if argv:
        print(__doc__)
        return 2
    counts = data.generate(Path.cwd())
    print(f"Wrote {len(counts)} files to data/raw/:")
    for name, rows in counts.items():
        print(f"  {name}.csv  {rows:,} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
